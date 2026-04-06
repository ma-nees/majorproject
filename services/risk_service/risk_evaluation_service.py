# services/risk_service/risk_evaluation_service.py
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import project modules
from ml_pipeline.model_registry.load_model import load_model
from ml_pipeline.feature_engineering import extract_features  # assuming you have this
from anomaly_detection.isolation_forest_detector import IsolationForestDetector
from anomaly_detection.behavior_monitor import GlobalBehaviorMonitor
from risk_engine.decision_engine import DecisionEngine, get_decision_engine
from services.alert_service.fraud_alerts import get_alert_manager
from monitoring.logging_config import get_logger

logger = get_logger(__name__)

class RiskEvaluationService:
    """
    Main service for evaluating transaction risk.
    Coordinates all components: feature extraction, ML scoring,
    anomaly detection, behavioral monitoring, risk engine, alerts.
    """
    
    def __init__(self,
                 ml_model_path: str = "models/xgboost.pkl",
                 if_model_path: str = "models/isolation_forest.pkl",
                 decision_engine: Optional[DecisionEngine] = None):
        """
        Initialize all detectors and models.
        """
        # Load supervised model (XGBoost, etc.)
        try:
            self.ml_model = load_model(ml_model_path)
            logger.info(f"Loaded ML model from {ml_model_path}")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.ml_model = None
        
        # Load unsupervised anomaly detector
        try:
            self.anomaly_detector = IsolationForestDetector(if_model_path)
            logger.info(f"Loaded Isolation Forest from {if_model_path}")
        except Exception as e:
            logger.error(f"Failed to load Isolation Forest: {e}")
            self.anomaly_detector = None
        
        # Behavioral monitor (stateful, singleton)
        self.behavior_monitor = GlobalBehaviorMonitor().get_monitor()
        
        # Risk decision engine
        self.decision_engine = decision_engine or get_decision_engine()
        
        # Alert manager
        self.alert_manager = get_alert_manager()
    
    async def evaluate_transaction(self,
                                    transaction: Dict[str, Any],
                                    trigger_alerts: bool = True) -> Dict[str, Any]:
        """
        Evaluate a single transaction and return risk decision.
        
        Args:
            transaction: dictionary containing transaction fields
            trigger_alerts: if True, send alerts for high-risk decisions
        
        Returns:
            decision dict from risk engine
        """
        try:
            # 1. Extract features for ML model
            features = self._extract_features(transaction)
            
            # 2. Get ML probability (if model available)
            ml_prob = 0.5  # default if model missing
            if self.ml_model is not None:
                try:
                    ml_prob = self.ml_model.predict_proba(features)[0][1]
                except Exception as e:
                    logger.error(f"ML prediction failed: {e}")
            
            # 3. Get anomaly score (0-100)
            anomaly_score = 50.0  # default
            if self.anomaly_detector is not None:
                try:
                    anomaly_score = self.anomaly_detector.get_risk_score(features)
                except Exception as e:
                    logger.error(f"Anomaly detection failed: {e}")
            
            # 4. Get behavioral risk score (0-100)
            # This also updates the user's history
            behavioral_risk = self._get_behavioral_risk(transaction)
            
            # 5. Run risk engine
            decision = self.decision_engine.evaluate_transaction(
                transaction=transaction,
                ml_probability=ml_prob,
                anomaly_score=anomaly_score,
                behavioral_risk=behavioral_risk
            )
            
            # 6. Trigger alerts if needed
            if trigger_alerts:
                await self._maybe_alert(decision)
            
            # 7. Log decision
            logger.info(f"Transaction {transaction.get('transaction_id')} -> "
                        f"{decision['action']} (risk={decision['risk_score']:.1f})")
            
            return decision
        
        except Exception as e:
            logger.exception(f"Risk evaluation failed for tx {transaction.get('transaction_id')}: {e}")
            # Return a safe fallback decision (e.g., REVIEW to be safe)
            return {
                "transaction_id": transaction.get("transaction_id", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "risk_score": 50.0,
                "fraud_probability": 0.5,
                "risk_level": "MEDIUM",
                "action": "REVIEW",
                "action_reason": "Service error, manual review required",
                "error": str(e)
            }
    
    async def evaluate_batch(self,
                             transactions: List[Dict[str, Any]],
                             trigger_alerts: bool = True) -> List[Dict[str, Any]]:
        """
        Evaluate multiple transactions (batch processing).
        Can be used for offline or high-throughput scenarios.
        """
        tasks = [self.evaluate_transaction(tx, trigger_alerts=trigger_alerts)
                 for tx in transactions]
        return await asyncio.gather(*tasks)
    
    def _extract_features(self, transaction: Dict[str, Any]) -> Any:
        """
        Call the feature engineering module to convert raw transaction
        into model-ready feature vector (numpy array or DataFrame).
        """
        # Import here to avoid circular imports
        from ml_pipeline.feature_engineering import extract_features as fe
        # Assume fe returns a 2D array (1 row)
        return fe(transaction)
    
    def _get_behavioral_risk(self, transaction: Dict[str, Any]) -> float:
        """
        Get behavioral risk score (0-100) and update user history.
        """
        # Extract needed fields
        user_id = transaction.get('user_id')
        if not user_id:
            return 0.0
        
        timestamp = transaction.get('timestamp')
        if isinstance(timestamp, str):
            from datetime import datetime
            timestamp = datetime.fromisoformat(timestamp)
        
        amount = transaction.get('amount', 0.0)
        location = transaction.get('location') or transaction.get('country_code')
        device_id = transaction.get('device_id')
        
        # Update and score
        risk = self.behavior_monitor.update_and_score(
            user_id=user_id,
            timestamp=timestamp,
            amount=amount,
            location=location,
            device_id=device_id
        )
        # Scale to 0-100 (behavior_monitor returns 0-1)
        return risk * 100.0
    
    async def _maybe_alert(self, decision: Dict[str, Any]):
        """Check if decision triggers an alert and send it."""
        alert = await self.alert_manager.check_transaction_risk(decision)
        if alert:
            await self.alert_manager.trigger_alert(alert)


# Singleton instance for use across API endpoints
_risk_service = None

def get_risk_service() -> RiskEvaluationService:
    global _risk_service
    if _risk_service is None:
        _risk_service = RiskEvaluationService()
    return _risk_service