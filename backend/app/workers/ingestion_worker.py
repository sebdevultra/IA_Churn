import os
import csv
import json
import threading
import time
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import SessionLocal
from backend.app.models.log import ProcessingLog
from backend.app.schemas.interaction import InteractionCreate
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.core.errors import DuplicateInteractionError, AppBaseException


_worker_lock = threading.Lock()


class IngestionWorker:
    """
    Automated Background Ingestion Worker.
    Scans incoming data files (CSV/JSON) and processes unhandled interactions.
    Thread-safe with mutual exclusion lock to prevent concurrent race conditions.
    """

    @classmethod
    def run_ingestion_job(cls) -> Dict[str, Any]:
        if not _worker_lock.acquire(blocking=False):
            logger.warning("Ingestion job skipped: another worker process is currently running.")
            return {"status": "SKIPPED", "reason": "Job is already running"}

        batch_id = f"batch-worker-{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        logger.info(f"--- Starting automated ingestion job [{batch_id}] ---")

        db: Session = SessionLocal()
        processed_count = 0
        duplicates_count = 0
        errors_count = 0

        try:
            # 1. First retry any stuck/pending interactions
            retried = IngestionPipelineService.retry_pending_interactions(db, max_batch=10)
            if retried > 0:
                logger.info(f"Retried and completed {retried} previously pending interactions.")

            # 2. Check for data files in watch directory
            watch_dir = settings.DATA_WATCH_DIR
            if os.path.exists(watch_dir):
                for filename in os.listdir(watch_dir):
                    filepath = os.path.join(watch_dir, filename)
                    if not os.path.isfile(filepath):
                        continue

                    # Process JSON files
                    if filename.endswith(".json"):
                        p, d, e = cls._process_json_file(db, filepath, batch_id)
                        processed_count += p
                        duplicates_count += d
                        errors_count += e

                    # Process CSV files
                    elif filename.endswith(".csv"):
                        p, d, e = cls._process_csv_file(db, filepath, batch_id)
                        processed_count += p
                        duplicates_count += d
                        errors_count += e

            duration_ms = (time.time() - start_time) * 1000
            # Record Batch Audit Log
            batch_log = ProcessingLog(
                batch_id=batch_id,
                step="BATCH_WORKER_EXECUTION",
                status="SUCCESS" if errors_count == 0 else "WARNING",
                records_processed=processed_count,
                duplicates_count=duplicates_count,
                errors_count=errors_count,
                duration_ms=duration_ms,
                details={
                    "retried_count": retried,
                    "processed_count": processed_count,
                    "duplicates_count": duplicates_count
                }
            )
            db.add(batch_log)
            db.commit()

            logger.info(
                f"--- Ingestion job [{batch_id}] finished in {duration_ms:.1f}ms: "
                f"{processed_count} processed, {duplicates_count} duplicates, {errors_count} errors ---"
            )
            return {
                "batch_id": batch_id,
                "processed": processed_count,
                "duplicates": duplicates_count,
                "errors": errors_count,
                "duration_ms": duration_ms
            }

        except Exception as exc:
            db.rollback()
            logger.exception(f"Fatal unhandled exception in IngestionWorker: {str(exc)}")
            return {"status": "ERROR", "error": str(exc)}
        finally:
            db.close()
            _worker_lock.release()

    @classmethod
    def _process_json_file(cls, db: Session, filepath: str, batch_id: str) -> (int, int, int):
        processed = 0
        duplicates = 0
        errors = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data = [data]

                for item in data:
                    try:
                        create_schema = InteractionCreate(
                            customer_external_id=item.get("customer_external_id") or item.get("customer_id", "CUST-UNKNOWN"),
                            source_type=item.get("source_type", "support_ticket"),
                            content=item.get("content", ""),
                            external_reference_id=item.get("external_reference_id") or item.get("id")
                        )
                        IngestionPipelineService.process_single_interaction(db, create_schema, batch_id=batch_id)
                        processed += 1
                    except DuplicateInteractionError:
                        duplicates += 1
                    except Exception as e:
                        errors += 1
                        logger.warning(f"Error processing item from {filepath}: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading JSON file {filepath}: {str(e)}")
            errors += 1

        return processed, duplicates, errors

    @classmethod
    def _process_csv_file(cls, db: Session, filepath: str, batch_id: str) -> (int, int, int):
        processed = 0
        duplicates = 0
        errors = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        create_schema = InteractionCreate(
                            customer_external_id=row.get("customer_external_id") or row.get("customer_id", "CUST-UNKNOWN"),
                            source_type=row.get("source_type", "support_ticket"),
                            content=row.get("content", ""),
                            external_reference_id=row.get("external_reference_id") or row.get("id")
                        )
                        IngestionPipelineService.process_single_interaction(db, create_schema, batch_id=batch_id)
                        processed += 1
                    except DuplicateInteractionError:
                        duplicates += 1
                    except Exception as e:
                        errors += 1
                        logger.warning(f"Error processing row from CSV {filepath}: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading CSV file {filepath}: {str(e)}")
            errors += 1

        return processed, duplicates, errors
