from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# api/schemas/transaction_schema.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TransactionEvaluateRequest(BaseModel):
    """Request body for single transaction evaluation."""
    transaction_id: Optional[str] = None
    user_id: str
    amount: float = Field(..., gt=0, le=1_000_000)
    timestamp: datetime
    location: Optional[str] = None
    country_code: Optional[str] = None
    device_id: Optional[str] = None
    # Add any other fields your model expects

    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

class TransactionResponse(BaseModel):
    """Response schema for stored transaction."""
    transaction_id: str
    user_id: str
    amount: float
    timestamp: datetime
    location: Optional[str] = None
    device_id: Optional[str] = None
    risk_score: Optional[float] = None
    fraud_probability: Optional[float] = None
    status: Optional[str] = None          # APPROVE, REVIEW, BLOCK, REJECTED
    risk_level: Optional[str] = None      # LOW, MEDIUM, HIGH, CRITICAL
    final_action: Optional[str] = None
    processed_at: datetime
    created_at: datetime
    is_fraud_actual: Optional[bool] = None

    class Config:
        orm_mode = True
        
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