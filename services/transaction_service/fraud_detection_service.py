def detect_fraud(amount: float):
    """
    Detect fraud based on transaction amount.
    
    Args:
        amount: Transaction amount
        
    Returns:
        Tuple of (risk_score, decision) where:
        - risk_score: Float between 0 and 1
        - decision: String either "approved" or "flagged"
    """
    # Simple heuristic-based fraud detection
    if amount > 10000:
        risk_score = 0.8
        decision = "flagged"
    elif amount > 5000:
        risk_score = 0.5
        decision = "review"
    else:
        risk_score = 0.1
        decision = "approved"
    
    return risk_score, decision
