# tests/test_models.py
import pytest
import numpy as np
from sklearn.ensemble import IsolationForest
from ml_pipeline.model_registry.load_model import load_model
from anomaly_detection.isolation_forest_detector import IsolationForestDetector

def test_load_model_missing():
    """Test that loading a non‑existent model raises an error."""
    with pytest.raises(Exception):
        load_model("nonexistent.pkl")

def test_isolation_forest_detector(tmp_path):
    """Test IsolationForest wrapper with a dummy model."""
    # Create a dummy model
    X_train = np.random.rand(100, 5)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    
    # Save to temporary path
    model_path = tmp_path / "if_model.pkl"
    import joblib
    joblib.dump(model, model_path)
    
    detector = IsolationForestDetector(str(model_path))
    test_sample = np.random.rand(1, 5)
    score = detector.get_risk_score(test_sample)
    assert 0 <= score <= 100
    
    pred = detector.predict_anomaly(test_sample)
    assert pred in [0, 1]

def test_metrics_calculation():
    """Test that FraudMetrics returns expected values."""
    from ml_pipeline.evaluation.metrics import FraudMetrics
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 0])
    y_proba = np.array([0.1, 0.9, 0.8, 0.4])
    
    evaluator = FraudMetrics(fraud_cost=100, review_cost=5)
    metrics = evaluator.calculate_all_metrics(y_true, y_pred, y_proba)
    
    assert metrics['recall'] == 0.5
    assert metrics['precision'] == 0.5
    assert metrics['roc_auc'] == 0.75
    assert 'cost_savings' in metrics