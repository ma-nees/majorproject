from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database.db_connection import get_db
from database import models
from api.schemas.transaction_schema import (
    FraudPredictionRequest, 
    FraudPredictionResponse,
    RiskLevel
)
from ml_pipeline.model_registry.load_model import load_fraud_model
from risk_engine.risk_score_calculator import calculate_risk_score
from anomaly_detection.isolation_forest_detector import detect_anomaly
from services.alert_service.fraud_alerts import create_alert_if_needed

router = APIRouter()

# Load ML model (cached)
fraud_model = None

def get_model():
    global fraud_model
    if fraud_model is None:
        fraud_model = load_fraud_model()
    return fraud_model

@router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(
    request: FraudPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a transaction for real-time fraud detection.
    """
    tx_data = request.transaction.dict()
    
    # Feature engineering (simplified - you'll expand)
    features = extract_features(tx_data, db)
    
    # ML prediction
    model = get_model()
    fraud_prob = model.predict_proba([features])[0][1]  # probability of fraud
    
    # Anomaly detection score
    anomaly_score = detect_anomaly(features)
    
    # Combine scores
    risk_score = calculate_risk_score(fraud_prob, anomaly_score, features)
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = RiskLevel.CRITICAL
        status = models.TransactionStatus.BLOCKED
    elif risk_score >= 0.4:
        risk_level = RiskLevel.HIGH
        status = models.TransactionStatus.FLAGGED
    elif risk_score >= 0.2:
        risk_level = RiskLevel.MEDIUM
        status = models.TransactionStatus.REVIEW
    else:
        risk_level = RiskLevel.LOW
        status = models.TransactionStatus.APPROVED
    
    # Save transaction to database
    transaction = models.Transaction(
        transaction_id=tx_data["transaction_id"],
        customer_id=tx_data["customer_id"],
        amount=tx_data["amount"],
        currency=tx_data.get("currency", "USD"),
        transaction_type=tx_data["transaction_type"],
        location=tx_data.get("location"),
        device_id=tx_data.get("device_id"),
        ip_address=tx_data.get("ip_address"),
        fraud_probability=fraud_prob,
        risk_score=risk_score,
        risk_level=risk_level,
        status=status,
        **features  # store engineered features
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Create alert if high risk
    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        background_tasks.add_task(
            create_alert_if_needed,
            transaction.transaction_id,
            risk_level,
            risk_score,
            db
        )
    
    # Prepare explanation (optional with SHAP/LIME)
    explanation = None  # You can integrate SHAP here
    
    return FraudPredictionResponse(
        transaction_id=tx_data["transaction_id"],
        is_fraud_predicted=fraud_prob > 0.5,
        fraud_probability=fraud_prob,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation
    )

def extract_features(tx_data, db):
    """
    Extract features from transaction and historical data.
    In production, this would be more sophisticated.
    """
    # Placeholder - implement real feature engineering
    import numpy as np
    from datetime import datetime
    
    now = datetime.now()
    hour = now.hour if tx_data.get("timestamp") is None else tx_data["timestamp"].hour
    
    # Count previous fraud for this customer
    prev_fraud = db.query(models.Transaction).filter(
        models.Transaction.customer_id == tx_data["customer_id"],
        models.Transaction.status == models.TransactionStatus.BLOCKED
    ).count()
    
    # Simple velocity: count transactions in last hour
    from datetime import timedelta
    one_hour_ago = now - timedelta(hours=1)
    velocity_1h = db.query(models.Transaction).filter(
        models.Transaction.customer_id == tx_data["customer_id"],
        models.Transaction.created_at >= one_hour_ago
    ).count()
    
    features = {
        "amount_normalized": min(tx_data["amount"] / 10000, 1.0),
        "hour_of_day": hour,
        "day_of_week": now.weekday(),
        "distance_from_usual": 0.0,  # would need user profile
        "velocity_1h": velocity_1h,
        "velocity_24h": 0,  # compute similarly
        "previous_fraud_count": prev_fraud,
    }
    return features