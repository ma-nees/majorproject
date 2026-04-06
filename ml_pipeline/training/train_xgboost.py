import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
import joblib
import os

def train_fraud_model(data_path: str = "data/processed/clean_transactions.csv"):
    """
    Train an XGBoost model for fraud detection.
    """
    # Load data
    df = pd.read_csv(data_path)
    
    # Feature engineering (expand as needed)
    features = [
        'amount', 'hour_of_day', 'day_of_week', 
        'velocity_1h', 'velocity_24h', 'previous_fraud_count',
        'distance_from_usual', 'transaction_type_encoded'
    ]
    
    # Encode categorical
    le = LabelEncoder()
    df['transaction_type_encoded'] = le.fit_transform(df['transaction_type'])
    
    # Prepare X, y
    X = df[features]
    y = df['is_fraud']
    
    # Scale numeric features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        scale_pos_weight=len(y_train[y_train==0])/len(y_train[y_train==1])  # handle imbalance
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Save model and artifacts
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/xgboost_fraud_model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(le, "models/label_encoder.pkl")
    
    # Evaluate
    from sklearn.metrics import classification_report, roc_auc_score
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")
    
    return model

if __name__ == "__main__":
    train_fraud_model()