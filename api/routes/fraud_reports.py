from fastapi import APIRouter
from database.db_connection import SessionLocal
from database.models import FraudAlert

router = APIRouter(
    prefix="/fraud-reports",
    tags=["Fraud Reports"]
)


@router.get("/")
def get_fraud_reports():

    db = SessionLocal()

    alerts = db.query(FraudAlert).all()

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }