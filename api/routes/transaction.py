from fastapi import APIRouter
from api.schemas.transaction_schema import TransactionRequest
from services.transaction_service.transaction_processor import process_transaction

router = APIRouter(
    prefix="/transaction",
    tags=["Transactions"]
)


@router.post("/")
def create_transaction(transaction: TransactionRequest):

    result = process_transaction(transaction.dict())

    return {
        "status": "processed",
        "result": result
    }