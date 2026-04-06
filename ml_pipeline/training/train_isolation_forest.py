# ml_pipeline/training/train_isolation_forest.py
from sklearn.ensemble import IsolationForest
import pandas as pd
import joblib
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml_pipeline.evaluation.metrics import FraudMetrics

def load_data(features_path: str, label_col: str = None):
    df = pd.read_csv(features_path)
    if label_col and label_col in df.columns:
        X = df.drop(columns=[label_col])
        y = df[label_col]
    else:
        X = df
        y = None
    return X, y

def train_isolation_forest(X_train, contamination='auto'):
    iso_forest = IsolationForest(
        n_estimators=100,
        max_samples='auto',
        contamination=contamination,
        random_state=42,
        behaviour='new'
    )
    iso_forest.fit(X_train)
    return iso_forest

def evaluate_iso_forest(model, X_val, y_val=None, fraud_cost=100.0, review_cost=5.0):
    preds = model.predict(X_val)
    y_pred = (preds == -1).astype(int)
    
    # Get anomaly scores (higher = more anomalous). Convert to probability-like for ROC.
    scores = model.decision_function(X_val)  # more negative = more anomalous
    y_proba = -scores  # now higher = more anomalous
    
    evaluator = FraudMetrics(fraud_cost=fraud_cost, review_cost=review_cost)
    if y_val is not None:
        metrics = evaluator.calculate_all_metrics(y_val, y_pred, y_proba)
        print(evaluator.generate_report(y_val, y_pred, y_proba))
        return metrics
    else:
        print("No labels provided for evaluation.")
        return {}

if __name__ == "__main__":
    DATA_PATH = "../../data/processed/features_train.csv"
    MODEL_PATH = "../../models/isolation_forest.pkl"
    METRICS_PATH = "../../models/iso_metrics.json"
    FRAUD_COST = 100.0
    REVIEW_COST = 5.0
    
    X, y = load_data(DATA_PATH, label_col='is_fraud')
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    actual_fraud_rate = y_train.mean() if y_train is not None else 0.01
    model = train_isolation_forest(X_train, contamination=actual_fraud_rate)
    
    metrics = evaluate_iso_forest(model, X_val, y_val, FRAUD_COST, REVIEW_COST)
    joblib.dump(model, MODEL_PATH)
    if metrics:
        with open(METRICS_PATH, 'w') as f:
            json.dump(metrics, f, indent=2)
    print(f"Isolation Forest saved to {MODEL_PATH}")