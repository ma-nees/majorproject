# ml_pipeline/training/train_logistic.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
import joblib
import json
import os
import sys

# Add project root to path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml_pipeline.evaluation.metrics import FraudMetrics, quick_metrics
from ml_pipeline.model_registry.save_model import save_model

def load_data(features_path: str, label_col: str = 'is_fraud'):
    df = pd.read_csv(features_path)
    X = df.drop(columns=[label_col])
    y = df[label_col]
    return X, y

def train_logistic(X_train, y_train, X_val, y_val, fraud_cost=100.0, review_cost=5.0):
    param_grid = {
        'C': [0.01, 0.1, 1, 10, 100],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear', 'saga'],
        'class_weight': ['balanced', None]
    }
    lr = LogisticRegression(max_iter=1000, random_state=42)
    grid = GridSearchCV(lr, param_grid, cv=3, scoring='recall', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_val)
    y_proba = best_model.predict_proba(X_val)[:, 1]
    
    # Use your metrics class
    evaluator = FraudMetrics(fraud_cost=fraud_cost, review_cost=review_cost)
    metrics = evaluator.calculate_all_metrics(y_val, y_pred, y_proba)
    
    print("Best params:", grid.best_params_)
    print(evaluator.generate_report(y_val, y_pred, y_proba))
    
    return best_model, metrics

if __name__ == "__main__":
    DATA_PATH = "../../data/processed/features_train.csv"
    MODEL_SAVE_PATH = "../../models/logistic_regression.pkl"
    METRICS_SAVE_PATH = "../../models/logistic_metrics.json"
    
    # Business costs – could come from config.yaml
    FRAUD_COST = 100.0   # cost of a missed fraud
    REVIEW_COST = 5.0    # cost of investigating a false positive
    
    X, y = load_data(DATA_PATH)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    model, metrics = train_logistic(X_train, y_train, X_val, y_val, 
                                    fraud_cost=FRAUD_COST, review_cost=REVIEW_COST)
    
    save_model(model, MODEL_SAVE_PATH)
    with open(METRICS_SAVE_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Model saved to {MODEL_SAVE_PATH}")