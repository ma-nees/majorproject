from fastapi import FastAPI
from api.routes import transaction, predict, fraud_reports
from api.middleware.authentication import AuthenticationMiddleware
from api.middleware.logging import LoggingMiddleware

app = FastAPI(
    title="Fraud Detection Platform API",
    description="API for detecting fraudulent transactions",
    version="1.0"
)

# Middleware
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(transaction.router)
app.include_router(predict.router)
app.include_router(fraud_reports.router)


@app.get("/")
def home():
    return {"message": "Fraud Detection Platform Running"}