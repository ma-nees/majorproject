# risk_engine/fraud_probability_mapper.py
import numpy as np
from typing import Dict, Tuple, Optional
from scipy.special import expit  # logistic function

class FraudProbabilityMapper:
    """
    Maps risk scores to calibrated fraud probabilities and action thresholds.
    Supports both linear and logistic mapping.
    """
    
    def __init__(self, mapping_type: str = 'logistic',
                 low_risk_threshold: float = 30.0,
                 medium_risk_threshold: float = 60.0,
                 high_risk_threshold: float = 85.0):
        """
        mapping_type: 'linear' or 'logistic'
        thresholds: risk score boundaries for decision actions.
        """
        self.mapping_type = mapping_type
        self.low_thresh = low_risk_threshold
        self.med_thresh = medium_risk_threshold
        self.high_thresh = high_risk_threshold
        
        # Logistic parameters (tune based on historical calibration)
        # Assumes risk_score 0 -> fraud_prob ~0.001, 50 -> 0.05, 100 -> 0.95
        self.logistic_scale = 0.1   # steepness
        self.logistic_offset = -5.0 # shift
    
    def risk_to_probability(self, risk_score: float) -> float:
        """Convert risk score (0-100) to fraud probability (0-1)."""
        if self.mapping_type == 'linear':
            # Simple linear: risk_score/100
            return risk_score / 100.0
        else:
            # Logistic: maps [0,100] -> [~0,1] with S-curve
            x = (risk_score - 50) * self.logistic_scale
            prob = expit(x + self.logistic_offset)
            # Ensure bounds
            return max(0.001, min(0.999, prob))
    
    def probability_to_risk(self, prob: float) -> float:
        """Inverse mapping (if needed)."""
        if self.mapping_type == 'linear':
            return prob * 100.0
        else:
            # Inverse logistic
            from scipy.special import logit
            x = logit(prob) - self.logistic_offset
            return (x / self.logistic_scale) + 50
    
    def get_action(self, risk_score: float) -> Tuple[str, str]:
        """
        Returns (action, reason) based on risk score thresholds.
        Actions: 'APPROVE', 'REVIEW', 'BLOCK'
        """
        if risk_score < self.low_thresh:
            return "APPROVE", "Low risk score"
        elif risk_score < self.med_thresh:
            return "REVIEW", "Medium risk – requires manual review"
        elif risk_score < self.high_thresh:
            return "REVIEW_PRIORITY", "High risk – prioritize review"
        else:
            return "BLOCK", "Critical risk – automatic decline"
    
    def get_decision_metadata(self, risk_score: float) -> Dict:
        """Return detailed decision info for logging/explainability."""
        prob = self.risk_to_probability(risk_score)
        action, reason = self.get_action(risk_score)
        return {
            "risk_score": round(risk_score, 2),
            "fraud_probability": round(prob, 4),
            "action": action,
            "reason": reason,
            "thresholds_used": {
                "low": self.low_thresh,
                "medium": self.med_thresh,
                "high": self.high_thresh
            }
        }


# You can also create a static mapper for use across the app
_default_mapper = None

def get_mapper() -> FraudProbabilityMapper:
    global _default_mapper
    if _default_mapper is None:
        _default_mapper = FraudProbabilityMapper()
    return _default_mapper