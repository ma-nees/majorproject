def process_transaction(transaction_data: dict):
    """
    Process a transaction and return the result.
    
    Args:
        transaction_data: Dictionary containing transaction details
        
    Returns:
        Dictionary with processing result
    """
    # Extract transaction details
    user_id = transaction_data.get('user_id')
    amount = transaction_data.get('amount')
    location = transaction_data.get('location')
    device = transaction_data.get('device')
    
    # Basic transaction processing logic
    result = {
        'user_id': user_id,
        'amount': amount,
        'location': location,
        'device': device,
        'processed': True
    }
    
    return result
