from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional

from database.db_connection import get_db
from database import models
from api.schemas.transaction_schema import AlertResponse, DashboardStatsResponse, RiskLevel

router = APIRouter()

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[RiskLevel] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(models.FraudAlert)
    if severity:
        query = query.filter(models.FraudAlert.severity == severity)
    if status:
        query = query.filter(models.FraudAlert.status == status)
    alerts = query.order_by(models.FraudAlert.created_at.desc()).limit(limit).all()
    return alerts

@router.patch("/alerts/{alert_id}")
def update_alert_status(alert_id: str, status: str, db: Session = Depends(get_db)):
    alert = db.query(models.FraudAlert).filter(models.FraudAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = status
    if status == "resolved":
        alert.resolved_at = datetime.now()
    db.commit()
    return {"message": "Alert updated"}

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    total_tx = db.query(models.Transaction).filter(models.Transaction.created_at >= week_ago).count()
    fraud_tx = db.query(models.Transaction).filter(
        models.Transaction.created_at >= week_ago,
        models.Transaction.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
    ).count()
    avg_risk = db.query(func.avg(models.Transaction.risk_score)).filter(
        models.Transaction.created_at >= week_ago
    ).scalar() or 0.0
    active_alerts = db.query(models.FraudAlert).filter(
        models.FraudAlert.status == "new"
    ).count()
    
    return DashboardStatsResponse(
        total_transactions=total_tx,
        fraud_detected=fraud_tx,
        risk_score=round(avg_risk * 100, 1),  # convert to 0-100 scale
        active_alerts=active_alerts
    )

@router.get("/analytics/trends")
def fraud_trends(period: str = "week", db: Session = Depends(get_db)):
    # Implement aggregation by day/week/month
    # Simplified example
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    results = db.query(
        func.date(models.Transaction.created_at).label("day"),
        func.count(models.Transaction.id).label("count")
    ).filter(
        models.Transaction.created_at >= start_date
    ).group_by("day").all()
    return [{"date": str(r.day), "fraud_cases": r.count} for r in results]