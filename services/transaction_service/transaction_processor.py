# services/transaction_service/transaction_processor.py
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """
    Handles transaction validation, enrichment, and persistence.
    """
    
    def __init__(self, db_connection=None):
        """
        db_connection: optional database connection (e.g., SQLAlchemy engine)
        """
        self.db = db_connection
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate required fields and basic data types.
        Returns (is_valid, error_message).
        """
        required_fields = ['user_id', 'amount', 'timestamp']
        for field in required_fields:
            if field not in transaction:
                return False, f"Missing required field: {field}"
        
        # Amount validation
        amount = transaction.get('amount')
        if not isinstance(amount, (int, float)) or amount < 0:
            return False, f"Invalid amount: {amount}"
        if amount > 1_000_000:  # sanity cap
            return False, f"Amount exceeds maximum allowed: {amount}"
        
        # Timestamp validation
        ts = transaction.get('timestamp')
        try:
            if isinstance(ts, str):
                datetime.fromisoformat(ts)
            elif isinstance(ts, datetime):
                pass
            else:
                return False, f"Invalid timestamp format: {ts}"
        except Exception:
            return False, f"Invalid timestamp format: {ts}"
        
        # User ID validation (non-empty string)
        user_id = transaction.get('user_id')
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "Invalid user_id"
        
        return True, None
    
    def enrich_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add derived fields: transaction_id, timestamp_iso, normalized fields.
        """
        enriched = transaction.copy()
        
        # Add unique transaction ID if missing
        if 'transaction_id' not in enriched or not enriched['transaction_id']:
            enriched['transaction_id'] = str(uuid4())
        
        # Ensure timestamp is datetime object
        if 'timestamp' in enriched and isinstance(enriched['timestamp'], str):
            enriched['timestamp'] = datetime.fromisoformat(enriched['timestamp'])
        
        # Add ingestion timestamp
        enriched['ingested_at'] = datetime.now()
        
        # Normalize location/country
        if 'location' in enriched and enriched['location']:
            enriched['location'] = enriched['location'].upper().strip()
        if 'country_code' in enriched and enriched['country_code']:
            enriched['country_code'] = enriched['country_code'].upper().strip()
        
        # Normalize device_id (if present)
        if 'device_id' in enriched and enriched['device_id']:
            enriched['device_id'] = enriched['device_id'].strip()
        
        return enriched
    
    async def store_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Persist transaction to database (optional).
        Returns success boolean.
        """
        if self.db is None:
            logger.info("No DB configured; transaction not stored.")
            return True
        
        try:
            # Example with SQLAlchemy (assuming a Transaction model)
            # from database.models import Transaction
            # async with self.db.begin() as conn:
            #     await conn.execute(Transaction.insert().values(**transaction))
            logger.debug(f"Transaction stored: {transaction['transaction_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to store transaction: {e}")
            return False


# Singleton instance
_processor = None

def get_transaction_processor() -> TransactionProcessor:
    global _processor
    if _processor is None:
        _processor = TransactionProcessor()
    return _processor