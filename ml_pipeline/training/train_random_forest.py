# ml_pipeline/training/train_random_forest.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import joblib
import json
import pandas as pd
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

def train_rf(X_train, y_train, X_val, y_val, fraud_cost=100.0, review_cost=5.0):
    param_dist = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'class_weight': ['balanced', 'balanced_subsample', None]
    }
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    random_search = RandomizedSearchCV(rf, param_dist, n_iter=20, cv=3, 
                                       scoring='recall', random_state=42, n_jobs=-1)
    random_search.fit(X_train, y_train)
    
    best_model = random_search.best_estimator_
    y_pred = best_model.predict(X_val)
    y_proba = best_model.predict_proba(X_val)[:, 1]
    
    evaluator = FraudMetrics(fraud_cost=fraud_cost, review_cost=review_cost)
    metrics = evaluator.calculate_all_metrics(y_val, y_pred, y_proba)
    
    print("Best params:", random_search.best_params_)
    print(evaluator.generate_report(y_val, y_pred, y_proba))
    
    # Feature importance
    feature_importance = pd.Series(best_model.feature_importances_, index=X_train.columns)
    print("\nTop 10 features:\n", feature_importance.nlargest(10))
    
    return best_model, metrics

if __name__ == "__main__":
    DATA_PATH = "../../data/processed/features_train.csv"
    MODEL_PATH = "../../models/random_forest.pkl"
    METRICS_PATH = "../../models/rf_metrics.json"
    FRAUD_COST = 100.0
    REVIEW_COST = 5.0
    
    X, y = load_data(DATA_PATH)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    model, metrics = train_rf(X_train, y_train, X_val, y_val, FRAUD_COST, REVIEW_COST)
    save_model(model, MODEL_PATH)
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)