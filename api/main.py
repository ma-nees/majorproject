from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
from api.middleware.logging import LoggingMiddleware
from api.middleware.authentication import oauth2_scheme

from database.db_connection import engine, Base, get_db
from api.routes import predict, transaction, fraud_reports
from api.middleware import authentication, logging as logging_middleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FraudShield API",
    description="AI-Powered Fraud Detection Platform",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(transaction.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(fraud_reports.router, prefix="/api/v1", tags=["Fraud Reports"])
app.add_middleware(LoggingMiddleware)
@app.get("/")
def root():
    return {"message": "FraudShield API is running", "status": "healthy"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except:
        db_status = "error"
    return {"status": "healthy", "database": db_status}