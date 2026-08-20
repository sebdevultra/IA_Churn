import hashlib
import re
from sqlalchemy.orm import Session
from backend.app.models.interaction import Interaction
from backend.app.core.logging import logger


class DeduplicationService:
    """
    Deduplication and Idempotency service.
    Generates deterministic SHA-256 hashes from normalized text and customer IDs
    to prevent processing duplicate interactions.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """Removes excessive whitespace, lowercase, and trims text."""
        if not text:
            return ""
        # Collapse multiple spaces, newlines and tabs into a single space
        normalized = re.sub(r"\s+", " ", text).strip().lower()
        return normalized

    @classmethod
    def generate_hash(cls, customer_external_id: str, content: str) -> str:
        """
        Creates a unique SHA-256 fingerprint for a customer's interaction.
        """
        clean_content = cls.normalize_text(content)
        clean_cust_id = customer_external_id.strip().upper()
        payload = f"{clean_cust_id}::{clean_content}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @classmethod
    def is_duplicate(cls, db: Session, interaction_hash: str) -> bool:
        """
        Checks if the interaction hash already exists in the database.
        """
        exists = db.query(Interaction.id).filter(Interaction.interaction_hash == interaction_hash).first() is not None
        if exists:
            logger.info(f"Duplicate interaction detected with hash: {interaction_hash}")
        return exists
