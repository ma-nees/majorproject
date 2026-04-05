from pydantic import BaseModel


class TransactionRequest(BaseModel):

    user_id: int
    amount: float
    location: str
    device: str