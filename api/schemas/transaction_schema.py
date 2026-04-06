from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    REVIEW = "review"

class TransactionCreate(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: Optional[str] = "USD"
    transaction_type: str
    location: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[datetime] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    amount: float
    fraud_probability: float
    risk_score: float
    risk_level: RiskLevel
    status: TransactionStatus
    created_at: datetime

class FraudPredictionRequest(BaseModel):
    transaction: TransactionCreate

class FraudPredictionResponse(BaseModel):
    transaction_id: str
    is_fraud_predicted: bool
    fraud_probability: float
    risk_score: float
    risk_level: RiskLevel
    explanation: Optional[dict] = None

class AlertResponse(BaseModel):
    alert_id: str
    alert_type: str
    severity: RiskLevel
    description: str
    status: str
    created_at: datetime

class DashboardStatsResponse(BaseModel):
    total_transactions: int
    fraud_detected: int
    risk_score: float
    active_alerts: int