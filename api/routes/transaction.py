from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from services.transaction_service.fraud_detection_service import get_fraud_detection_service
from database.db_connection import get_db
from database import models
from api.schemas.transaction_schema import TransactionResponse, TransactionEvaluateRequest

router = APIRouter()

@router.post("/transaction/evaluate")
async def evaluate_transaction(transaction: TransactionEvaluateRequest):
    """
    Submit a transaction for fraud detection.
    Accepts a validated request body (Pydantic model).
    """
    service = get_fraud_detection_service()
    # Convert Pydantic model to dict
    result = await service.detect_fraud(transaction.dict(), store_result=True, trigger_alerts=True)
    if result.get("status") == "REJECTED":
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/transaction/batch")
async def batch_evaluate(transactions: List[TransactionEvaluateRequest]):
    """
    Submit multiple transactions.
    """
    service = get_fraud_detection_service()
    tx_dicts = [tx.dict() for tx in transactions]
    results = await service.process_batch(tx_dicts, store_result=False, trigger_alerts=False)
    return results

@router.post("/transaction/feedback")
async def feedback(transaction_id: str, was_fraud: bool):
    """
    Update ground truth after manual review or chargeback.
    """
    service = get_fraud_detection_service()
    await service.update_with_feedback(transaction_id, was_fraud)
    return {"status": "ok"}

@router.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction)
    if risk_level:
        query = query.filter(models.Transaction.risk_level == risk_level)
    if status:
        query = query.filter(models.Transaction.status == status)
    transactions = query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx