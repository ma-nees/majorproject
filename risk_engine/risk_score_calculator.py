# risk_engine/risk_score_calculator.py
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class RiskComponents:
    """Individual risk scores (0-100) from different sources."""
    ml_score: float          # from supervised model (e.g., XGBoost probability * 100)
    anomaly_score: float     # from Isolation Forest / LOF (0-100)
    behavioral_score: float  # from behavioral_biometrics / behavior monitor
    rule_score: float        # from rule_based_checks (0-100, 0=no rule fired)
    
    # Optional weights can be overridden per transaction type
    weight_ml: float = 0.4
    weight_anomaly: float = 0.3
    weight_behavioral: float = 0.2
    weight_rules: float = 0.1

class RiskScoreCalculator:
    """
    Combines multiple risk signals into a final risk score (0-100).
    Supports dynamic weighting and optional boosting for high-risk signals.
    """
    
    def __init__(self, default_weights: Optional[Dict[str, float]] = None):
        """
        default_weights: dict with keys 'ml', 'anomaly', 'behavioral', 'rules'
        """
        self.default_weights = default_weights or {
            'ml': 0.4,
            'anomaly': 0.3,
            'behavioral': 0.2,
            'rules': 0.1
        }
    
    def calculate(self, components: RiskComponents) -> float:
        """
        Weighted average of risk components, each already in [0,100].
        Returns final risk score (0-100).
        """
        # Use components' own weights if provided, else defaults
        w_ml = components.weight_ml if hasattr(components, 'weight_ml') else self.default_weights['ml']
        w_anom = components.weight_anomaly if hasattr(components, 'weight_anomaly') else self.default_weights['anomaly']
        w_behav = components.weight_behavioral if hasattr(components, 'weight_behavioral') else self.default_weights['behavioral']
        w_rules = components.weight_rules if hasattr(components, 'weight_rules') else self.default_weights['rules']
        
        total_weight = w_ml + w_anom + w_behav + w_rules
        if total_weight == 0:
            return 0.0
        
        score = (components.ml_score * w_ml +
                 components.anomaly_score * w_anom +
                 components.behavioral_score * w_behav +
                 components.rule_score * w_rules) / total_weight
        
        # Clip to [0,100]
        return max(0.0, min(100.0, score))
    
    def calculate_with_boosting(self, components: RiskComponents,
                                 boost_threshold: float = 80.0,
                                 boost_factor: float = 1.2) -> float:
        """
        Same as calculate, but if any component exceeds boost_threshold,
        apply boost_factor to the final score (capped at 100).
        Useful when a single signal is extremely strong.
        """
        base_score = self.calculate(components)
        max_component = max(components.ml_score, components.anomaly_score,
                            components.behavioral_score, components.rule_score)
        if max_component >= boost_threshold:
            base_score = min(100.0, base_score * boost_factor)
        return base_score
    
    def get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level."""
        if score < 30:
            return "LOW"
        elif score < 60:
            return "MEDIUM"
        elif score < 85:
            return "HIGH"
        else:
            return "CRITICAL"


# Example integration with other modules
def build_risk_components_from_transaction(transaction: Dict[str, Any],
                                            ml_probability: float,
                                            anomaly_raw_score: float,
                                            behavioral_risk: float,
                                            rule_violations: List[str]) -> RiskComponents:
    """
    Helper to create RiskComponents from various detector outputs.
    Assumes ml_probability in [0,1], anomaly_raw_score can be any range,
    behavioral_risk in [0,100], rule_violations list.
    """
    # Convert ML probability to 0-100
    ml_score = ml_probability * 100.0
    
    # Convert anomaly score (e.g., from Isolation Forest decision_function) to 0-100
    # This depends on your normalization in anomaly_detection; assume already 0-100.
    anomaly_score = anomaly_raw_score if isinstance(anomaly_raw_score, (int, float)) else 50.0
    
    # Rule score: 0 if no violations, else increase based on number/severity
    rule_score = min(100.0, len(rule_violations) * 20.0) if rule_violations else 0.0
    
    return RiskComponents(
        ml_score=ml_score,
        anomaly_score=anomaly_score,
        behavioral_score=behavioral_risk,
        rule_score=rule_score
    )