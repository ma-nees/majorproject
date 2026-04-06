# services/transaction_service/fraud_detection_service.py
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from services.transaction_service.transaction_processor import get_transaction_processor
from services.risk_service.risk_evaluation_service import get_risk_service
from monitoring.logging_config import get_logger
from monitoring.fraud_metrics import get_metrics_tracker

logger = get_logger(__name__)

class FraudDetectionService:
    """
    Main entry point for fraud detection on a transaction.
    Handles validation, enrichment, risk evaluation, and post-processing.
    """
    
    def __init__(self):
        self.processor = get_transaction_processor()
        self.risk_service = get_risk_service()
        self.metrics_tracker = get_metrics_tracker()
    
    async def detect_fraud(self,
                           transaction: Dict[str, Any],
                           store_result: bool = True,
                           trigger_alerts: bool = True) -> Dict[str, Any]:
        """
        Full fraud detection pipeline for a single transaction.
        
        Returns:
            decision dict with added fields like 'status', 'processed_at'
        """
        # 1. Validate
        is_valid, error = self.processor.validate_transaction(transaction)
        if not is_valid:
            logger.warning(f"Invalid transaction: {error}")
            return {
                "transaction_id": transaction.get('transaction_id', 'unknown'),
                "status": "REJECTED",
                "error": error,
                "processed_at": datetime.now().isoformat()
            }
        
        # 2. Enrich
        enriched_tx = self.processor.enrich_transaction(transaction)
        
        # 3. Evaluate risk (async call)
        decision = await self.risk_service.evaluate_transaction(
            enriched_tx,
            trigger_alerts=trigger_alerts
        )
        
        # 4. Add transaction status and timestamps
        decision['status'] = decision.get('action')  # APPROVE, REVIEW, BLOCK, etc.
        decision['processed_at'] = datetime.now().isoformat()
        decision['enriched_transaction'] = enriched_tx  # for audit
        
        # 5. Store transaction (if requested)
        if store_result:
            await self.processor.store_transaction({
                **enriched_tx,
                "risk_score": decision.get('risk_score'),
                "fraud_probability": decision.get('fraud_probability'),
                "final_action": decision.get('action'),
                "processed_at": decision['processed_at']
            })
        
        # 6. Optionally log ground truth later (if we get chargeback feedback)
        # This would be done via another endpoint (e.g., feedback)
        
        return decision
    
    async def process_batch(self,
                            transactions: list,
                            store_result: bool = True,
                            trigger_alerts: bool = False) -> list:
        """
        Process multiple transactions concurrently.
        Alerts are usually disabled for batch to avoid spam.
        """
        import asyncio
        tasks = [self.detect_fraud(tx, store_result, trigger_alerts) for tx in transactions]
        return await asyncio.gather(*tasks)
    
    async def update_with_feedback(self, transaction_id: str, was_fraud: bool):
        """
        After chargeback or manual review, update ground truth.
        This allows tracking model performance over time.
        """
        # This would update the predictions log with the true label
        # For simplicity, you could store in a separate table
        logger.info(f"Feedback for tx {transaction_id}: fraud={was_fraud}")
        # Example: update predictions_log.csv via metrics_tracker
        # (You'd need to implement a method to update by transaction_id)
        # self.metrics_tracker.update_label(transaction_id, was_fraud)


# Singleton
_detection_service = None

def get_fraud_detection_service() -> FraudDetectionService:
    global _detection_service
    if _detection_service is None:
        _detection_service = FraudDetectionService()
    return _detection_service