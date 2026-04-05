from fastapi import APIRouter
from api.schemas.transaction_schema import TransactionRequest
from services.transaction_service.fraud_detection_service import detect_fraud

router = APIRouter(
    prefix="/predict",
    tags=["Fraud Prediction"]
)


@router.post("/")
def predict_fraud(transaction: TransactionRequest):

    risk_score, decision = detect_fraud(transaction.amount)

    return {
        "risk_score": risk_score,
        "decision": decision
    }