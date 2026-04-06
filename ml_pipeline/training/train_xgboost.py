# ml_pipeline/training/train_xgboost.py
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml_pipeline.evaluation.metrics import FraudMetrics
from ml_pipeline.model_registry.save_model import save_model

def load_data(features_path: str, label_col: str = 'is_fraud'):
    df = pd.read_csv(features_path)
    X = df.drop(columns=[label_col])
    y = df[label_col]
    return X, y

def train_xgboost(X_train, y_train, X_val, y_val, fraud_cost=100.0, review_cost=5.0):
    scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [4, 6, 8],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'scale_pos_weight': [scale_pos_weight]
    }
    
    xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False)
    grid = GridSearchCV(xgb_model, param_grid, cv=3, scoring='recall', n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_val)
    y_proba = best_model.predict_proba(X_val)[:, 1]
    
    evaluator = FraudMetrics(fraud_cost=fraud_cost, review_cost=review_cost)
    metrics = evaluator.calculate_all_metrics(y_val, y_pred, y_proba)
    
    print("Best params:", grid.best_params_)
    print(evaluator.generate_report(y_val, y_pred, y_proba))
    
    return best_model, metrics

if __name__ == "__main__":
    DATA_PATH = "../../data/processed/features_train.csv"
    MODEL_PATH = "../../models/xgboost.pkl"
    METRICS_PATH = "../../models/xgboost_metrics.json"
    FRAUD_COST = 100.0
    REVIEW_COST = 5.0
    
    X, y = load_data(DATA_PATH)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    model, metrics = train_xgboost(X_train, y_train, X_val, y_val, FRAUD_COST, REVIEW_COST)
    save_model(model, MODEL_PATH)
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)