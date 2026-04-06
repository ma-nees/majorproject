# ml_pipeline/preprocessing/clean_data.py
import pandas as pd
import numpy as np
import re
from typing import Dict, Any

def clean_transaction_data(df: pd.DataFrame, is_streaming: bool = False) -> pd.DataFrame:
    """
    Clean raw transaction data.
    - is_streaming: if True, skip expensive operations like sorting.
    """
    df = df.copy()
    
    # --- 1. Remove duplicate transaction IDs (both exact and near-duplicate time+amount+user)
    if 'transaction_id' in df.columns:
        df = df.drop_duplicates(subset=['transaction_id'], keep='first')
    # Optional: fuzzy duplicate detection (same user, amount, timestamp within 1s)
    if {'user_id', 'amount', 'timestamp'}.issubset(df.columns):
        df['timestamp_floor'] = pd.to_datetime(df['timestamp']).dt.floor('s')
        dup_mask = df.duplicated(subset=['user_id', 'amount', 'timestamp_floor'], keep='first')
        df = df[~dup_mask].drop(columns=['timestamp_floor'])
    
    # --- 2. Timestamp handling
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        if not is_streaming:
            df = df.sort_values('timestamp').reset_index(drop=True)
    
    # --- 3. Outlier capping for amount (per user if user_id exists)
    if 'amount' in df.columns:
        if 'user_id' in df.columns and not is_streaming:
            # User-specific capping (better for fraud)
            df['amount'] = df.groupby('user_id')['amount'].transform(
                lambda x: x.clip(upper=x.quantile(0.999)) if len(x) > 10 else x
            )
        else:
            # Global cap
            upper = df['amount'].quantile(0.999)
            df['amount'] = df['amount'].clip(upper=upper)
    
    # --- 4. Standardise categorical fields
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        if col not in ['transaction_id', 'timestamp']:
            df[col] = df[col].astype(str).str.strip().str.lower()
            # Replace empty strings with 'missing'
            df[col] = df[col].replace(r'^\s*$', 'missing', regex=True)
    
    # --- 5. Remove obviously invalid rows (negative amount, future timestamp)
    if 'amount' in df.columns:
        df = df[df['amount'] >= 0]
    if 'timestamp' in df.columns:
        df = df[df['timestamp'] <= pd.Timestamp.now()]
    
    return df