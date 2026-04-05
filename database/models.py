from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from database.db_connection import Base


class FraudAlert(Base):
    """Database model for fraud alerts"""
    __tablename__ = "fraud_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    amount = Column(Float)
    location = Column(String)
    device = Column(String)
    risk_score = Column(Float)
    decision = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_confirmed = Column(Boolean, default=False)
