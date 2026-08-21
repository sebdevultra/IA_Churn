import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.workers.ingestion_worker import IngestionWorker


scheduler = BackgroundScheduler()


def start_scheduler():
    """Initializes and starts the periodic automation worker."""
    if not settings.SCHEDULER_ENABLED:
        logger.info("APScheduler is disabled by configuration (SCHEDULER_ENABLED=false).")
        return

    if scheduler.running:
        logger.info("APScheduler is already running.")
        return

    try:
        scheduler.add_job(
            func=IngestionWorker.run_ingestion_job,
            trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
            id="periodic_ingestion_job",
            name="Periodic Ingestion & Churn Analysis Job",
            replace_existing=True,
            max_instances=1
        )
        scheduler.start()
        logger.info(f"APScheduler started successfully. Running every {settings.SCHEDULER_INTERVAL_MINUTES} minutes.")

        # Run once on startup in a separate daemon thread if auto-ingest is enabled
        if settings.AUTO_INGEST_SAMPLE_DATA:
            logger.info("Triggering initial bootstrap ingestion run...")
            t = threading.Thread(target=IngestionWorker.run_ingestion_job, name="bootstrap_ingest", daemon=True)
            t.start()

    except Exception as e:
        logger.error(f"Failed to start APScheduler: {str(e)}")


def shutdown_scheduler():
    """Gracefully shuts down the background scheduler."""
    if scheduler.running:
        logger.info("Shutting down APScheduler...")
        try:
            scheduler.shutdown(wait=False)
        except Exception as e:
            logger.warning(f"Error during scheduler shutdown: {str(e)}")
        logger.info("APScheduler stopped.")


def trigger_immediate_job():
    """Manually triggers the ingestion job on demand."""
    logger.info("Manual ingestion job triggered via API.")
    return IngestionWorker.run_ingestion_job()
