# tests/conftest.py
import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from database.db_connection import get_db
from database import models
from services.risk_service.risk_evaluation_service import RiskEvaluationService
from risk_engine.decision_engine import DecisionEngine

# ---------- Database fixtures ----------
@pytest.fixture(scope="session")
def db_engine():
    """In‑memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    """Yield a new database session for each test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def override_get_db(db_session):
    """Override the dependency in FastAPI to use test DB."""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db

# ---------- FastAPI test client ----------
@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ---------- Mock risk service (optional) ----------
@pytest.fixture
def mock_risk_service(monkeypatch):
    """Replace real risk evaluation with a predictable mock."""
    async def mock_evaluate(tx, trigger_alerts=True):
        return {
            "transaction_id": tx.get("transaction_id", "mock"),
            "risk_score": 75.0,
            "fraud_probability": 0.75,
            "risk_level": "HIGH",
            "action": "REVIEW",
            "status": "REVIEW",
            "processed_at": "2025-01-01T00:00:00"
        }
    monkeypatch.setattr(
        "services.risk_service.risk_evaluation_service.RiskEvaluationService.evaluate_transaction",
        mock_evaluate
    )

# ---------- Sample transaction fixture ----------
@pytest.fixture
def sample_transaction():
    return {
        "user_id": "test_user_123",
        "amount": 1500.0,
        "timestamp": "2025-01-15T10:30:00",
        "location": "US",
        "device_id": "device_abc"
    }