# risk_engine/decision_engine.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .risk_score_calculator import RiskScoreCalculator, RiskComponents, build_risk_components_from_transaction
from .fraud_probability_mapper import FraudProbabilityMapper, get_mapper
from .rule_based_checks import RuleBasedChecker, get_rule_checker

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Main entry point for risk evaluation.
    Combines all signals, applies rules, and returns final decision.
    """
    
    def __init__(self,
                 calculator: Optional[RiskScoreCalculator] = None,
                 mapper: Optional[FraudProbabilityMapper] = None,
                 rule_checker: Optional[RuleBasedChecker] = None):
        self.calculator = calculator or RiskScoreCalculator()
        self.mapper = mapper or get_mapper()
        self.rule_checker = rule_checker or get_rule_checker()
    
    def evaluate_transaction(self,
                             transaction: Dict[str, Any],
                             ml_probability: float,
                             anomaly_score: float,
                             behavioral_risk: float) -> Dict[str, Any]:
        """
        Full evaluation pipeline.
        
        Args:
            transaction: raw transaction dict (must contain user_id, amount, etc.)
            ml_probability: supervised model output (0-1)
            anomaly_score: unsupervised anomaly score (0-100, higher=more anomalous)
            behavioral_risk: behavioral risk score (0-100)
        
        Returns:
            Decision dict with action, risk score, probability, triggered rules, etc.
        """
        # 1. Run rule-based checks
        rule_violations = self.rule_checker.check_all(transaction)
        rule_score = self.rule_checker.calculate_rule_score(rule_violations)
        
        # 2. Build risk components
        components = build_risk_components_from_transaction(
            transaction, ml_probability, anomaly_score, behavioral_risk, rule_violations
        )
        
        # 3. Calculate final risk score
        risk_score = self.calculator.calculate(components)
        risk_level = self.calculator.get_risk_level(risk_score)
        
        # 4. Map to probability and action
        fraud_prob = self.mapper.risk_to_probability(risk_score)
        action, action_reason = self.mapper.get_action(risk_score)
        
        # 5. Apply hard overrides (e.g., if rule explicitly says BLOCK)
        if "BLOCK" in rule_violations:
            action = "BLOCK"
            action_reason = "Hard rule triggered: " + ", ".join(rule_violations)
        elif "REVIEW" in rule_violations and action == "APPROVE":
            action = "REVIEW"
            action_reason = "Rule triggered manual review"
        
        # 6. Prepare response
        decision = {
            "transaction_id": transaction.get("transaction_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "risk_score": round(risk_score, 2),
            "fraud_probability": round(fraud_prob, 4),
            "risk_level": risk_level,
            "action": action,
            "action_reason": action_reason,
            "triggered_rules": rule_violations,
            "components": {
                "ml_score": components.ml_score,
                "anomaly_score": components.anomaly_score,
                "behavioral_score": components.behavioral_score,
                "rule_score": components.rule_score,
            }
        }
        
        logger.info(f"Decision for tx {transaction.get('transaction_id')}: {action} (risk={risk_score:.1f})")
        return decision


# Singleton for service use
_decision_engine = None

def get_decision_engine() -> DecisionEngine:
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionEngine()
    return _decision_engine