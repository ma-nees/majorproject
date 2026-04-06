from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.sql import func
from database.db_connection import Base
import enum

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    REVIEW = "review"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    transaction_type = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    location = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    
    # Features used by ML
    amount_normalized = Column(Float)
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    distance_from_usual = Column(Float)
    velocity_1h = Column(Integer, default=0)
    velocity_24h = Column(Integer, default=0)
    previous_fraud_count = Column(Integer, default=0)
    
    # Prediction results
    fraud_probability = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    transaction_id = Column(String, index=True, foreign_key="transactions.transaction_id")
    alert_type = Column(String)  # e.g., "unusual_amount", "velocity_check", "geolocation_mismatch"
    severity = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    description = Column(Text)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)
    risk_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class BehavioralSession(Base):
    __tablename__ = "behavioral_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    keystroke_pattern = Column(JSON, nullable=True)
    mouse_movements = Column(JSON, nullable=True)
    touch_pattern = Column(JSON, nullable=True)
    behavioral_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())