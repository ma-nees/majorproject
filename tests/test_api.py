# tests/test_api.py
import pytest
from fastapi import status

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

def test_evaluate_transaction(client, sample_transaction):
    """Test the transaction evaluation endpoint."""
    response = client.post("/api/v1/transaction/evaluate", json=sample_transaction)
    # If real service is used, we just check response structure
    assert response.status_code == 200
    data = response.json()
    assert "action" in data
    assert "risk_score" in data

def test_evaluate_transaction_invalid(client):
    """Test invalid transaction (missing amount)."""
    invalid_tx = {"user_id": "user", "timestamp": "2025-01-01T00:00:00"}
    response = client.post("/api/v1/transaction/evaluate", json=invalid_tx)
    assert response.status_code == 400  # validation error

def test_list_transactions(client, db_session, sample_transaction):
    """Test GET /transactions returns paginated list."""
    # Insert a test transaction
    from database import models
    from datetime import datetime
    tx = models.Transaction(
        transaction_id="test123",
        user_id="user1",
        amount=100,
        timestamp=datetime.now(),
        status="APPROVE",
        risk_level="LOW",
        final_action="APPROVE",
        processed_at=datetime.now()
    )
    db_session.add(tx)
    db_session.commit()
    
    response = client.get("/api/v1/transactions?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "transaction_id" in data[0]

def test_get_transaction_by_id(client, db_session):
    """Test GET /transactions/{id} returns correct transaction."""
    from database import models
    from datetime import datetime
    tx = models.Transaction(
        transaction_id="tx_001",
        user_id="user2",
        amount=200,
        timestamp=datetime.now(),
        status="REVIEW",
        risk_level="MEDIUM",
        final_action="REVIEW",
        processed_at=datetime.now()
    )
    db_session.add(tx)
    db_session.commit()
    
    response = client.get("/api/v1/transactions/tx_001")
    assert response.status_code == 200
    assert response.json()["transaction_id"] == "tx_001"
    
    # Non‑existent
    response = client.get("/api/v1/transactions/unknown")
    assert response.status_code == 404