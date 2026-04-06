# tests/test_risk_engine.py
import pytest
import numpy as np
from datetime import datetime
from risk_engine.risk_score_calculator import RiskScoreCalculator, RiskComponents
from risk_engine.fraud_probability_mapper import FraudProbabilityMapper
from risk_engine.rule_based_checks import RuleBasedChecker
from risk_engine.decision_engine import DecisionEngine

def test_risk_score_calculator():
    calc = RiskScoreCalculator(default_weights={'ml':0.5, 'anomaly':0.3, 'behavioral':0.2, 'rules':0.0})
    components = RiskComponents(
        ml_score=80.0,
        anomaly_score=60.0,
        behavioral_score=40.0,
        rule_score=0.0
    )
    score = calc.calculate(components)
    assert 0 <= score <= 100
    # weighted average: (80*0.5 + 60*0.3 + 40*0.2) = 40+18+8 = 66
    assert score == 66.0

def test_risk_score_boosting():
    calc = RiskScoreCalculator()
    components = RiskComponents(
        ml_score=95.0, anomaly_score=50.0, behavioral_score=50.0, rule_score=0.0
    )
    normal = calc.calculate(components)
    boosted = calc.calculate_with_boosting(components, boost_threshold=90, boost_factor=1.2)
    assert boosted >= normal
    assert boosted <= 100

def test_fraud_probability_mapper():
    mapper = FraudProbabilityMapper(mapping_type='logistic', low_risk_threshold=30, medium_risk_threshold=60, high_risk_threshold=85)
    # Test mapping
    prob = mapper.risk_to_probability(0)
    assert 0 <= prob <= 1
    prob_high = mapper.risk_to_probability(100)
    assert prob_high > 0.9
    
    action, reason = mapper.get_action(90)
    assert action == "BLOCK"
    action, reason = mapper.get_action(50)
    assert action == "REVIEW"

def test_rule_based_checker():
    checker = RuleBasedChecker({
        'max_amount_normal': 5000,
        'max_amount_suspicious': 20000,
        'blacklisted_countries': ['XX'],
        'blacklisted_devices': ['bad_device']
    })
    tx = {'amount': 10000, 'country_code': 'US', 'device_id': 'good'}
    violations = checker.check_all(tx)
    # amount > 5000 -> AMOUNT_HIGH
    assert any('AMOUNT_HIGH' in v for v in violations)
    
    tx2 = {'amount': 30000, 'country_code': 'XX', 'device_id': 'bad_device'}
    violations2 = checker.check_all(tx2)
    assert any('AMOUNT_EXTREME' in v for v in violations2)
    assert any('BLACKLISTED_COUNTRY' in v for v in violations2)
    assert any('BLACKLISTED_DEVICE' in v for v in violations2)

def test_rule_score():
    checker = RuleBasedChecker()
    violations = ["AMOUNT_HIGH", "VELOCITY_HIGH"]
    score = checker.calculate_rule_score(violations)
    # 25 + 25 = 50
    assert score == 50.0

def test_decision_engine_integration(monkeypatch):
    """Test the full decision pipeline with mocked components."""
    # Mock rule checker to always return a fixed violation
    def mock_check_all(tx):
        return ["TEST_RULE"]
    def mock_calculate_rule_score(violations):
        return 30.0
    
    monkeypatch.setattr("risk_engine.rule_based_checks.RuleBasedChecker.check_all", mock_check_all)
    monkeypatch.setattr("risk_engine.rule_based_checks.RuleBasedChecker.calculate_rule_score", mock_calculate_rule_score)
    
    engine = DecisionEngine()
    decision = engine.evaluate_transaction(
        transaction={"transaction_id": "t1", "user_id": "u1", "amount": 100},
        ml_probability=0.8,
        anomaly_score=70.0,
        behavioral_risk=50.0
    )
    assert decision["action"] in ["APPROVE", "REVIEW", "BLOCK"]
    assert "triggered_rules" in decision
    assert "TEST_RULE" in decision["triggered_rules"]