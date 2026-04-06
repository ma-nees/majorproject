from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
from api.middleware.logging import LoggingMiddleware
from api.middleware.authentication import oauth2_scheme


from monitoring.logging_config import setup_logging, get_logger
from monitoring.system_metrics import get_system_collector, system_metrics_middleware
from monitoring.fraud_metrics import get_metrics_tracker
from database.db_connection import engine, Base, get_db
from api.routes import predict, transaction, fraud_reports

from monitoring.logging_config import setup_logging
from monitoring.system_metrics import get_system_collector, system_metrics_middleware
from monitoring.fraud_metrics import get_metrics_tracker
from database.db_connection import engine, Base, get_db
from api.routes import predict, transaction, fraud_reports
from api.middleware import authentication, logging as logging_middleware


from api.middleware.logging import http_logging_middleware
app.middleware("http")(http_logging_middleware)
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

app = FastAPI()

# Setup logging
setup_logging(log_level="INFO", log_to_file=True, log_to_console=True, json_format=False)

# Add system metrics middleware
app.middleware("http")(system_metrics_middleware)

@app.on_event("startup")
async def startup_event():
    get_system_collector()  # start background sampling
    get_metrics_tracker()   # initialize tracker
    logger = get_logger("api")
    logger.info("Fraud detection platform started")
# Database
from database.db_connection import engine, Base, get_db

# API routes
from api.routes import transaction, fraud_reports
# from api.routes import predict   # uncomment when predict.py exists

# Create database tables (if not exists)
Base.metadata.create_all(bind=engine)

# Setup logging (must be done before any other logging calls)
setup_logging(log_level="INFO", log_to_file=True, log_to_console=True, json_format=False)

# Initialize FastAPI app
app = FastAPI(
    title="FraudShield API",
    description="AI-Powered Fraud Detection Platform",
    version="1.0.0"
)

# CORS middleware (allow frontend origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware (after CORS)
app.add_middleware(system_metrics_middleware)  # wraps each request

# Include routers
app.include_router(transaction.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(fraud_reports.router, prefix="/api/v1", tags=["Fraud Reports"])
# app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])  # uncomment later

# Root endpoint
@app.get("/")
def root():
    return {"message": "FraudShield API is running", "status": "healthy"}

# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Simple database connectivity check
    try:
        # Use a simple query that works with most SQL databases
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger = get_logger("api")
        logger.error(f"Health check DB error: {e}")
    return {"status": "healthy", "database": db_status}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Start system metrics collector (background sampling)
    get_system_collector()
    # Initialize metrics tracker (creates storage directories)
    get_metrics_tracker()
    # Log startup
    logger = get_logger("api")
    logger.info("FraudShield platform started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger = get_logger("api")
    logger.info("FraudShield platform shutting down")