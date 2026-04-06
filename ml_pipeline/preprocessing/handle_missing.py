# ml_pipeline/preprocessing/handle_missing.py
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, Any

# Global dictionary to store imputation parameters (fit during training)
_IMPUTATION_PARAMS = {}

def fit_imputation_params(df: pd.DataFrame, save_path: str = None) -> Dict[str, Any]:
    """Learn imputation values from training data and optionally save to JSON."""
    params = {}
    # Numerical: median for amount-like, -1 for count-like (but store median anyway)
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if col == 'amount' or 'avg' in col or 'std' in col:
            params[col] = {'type': 'median', 'value': df[col].median()}
        else:
            params[col] = {'type': 'constant', 'value': -1}
    
    # Categorical: mode or 'missing'
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        mode_val = df[col].mode()
        if len(mode_val) > 0:
            params[col] = {'type': 'mode', 'value': mode_val[0]}
        else:
            params[col] = {'type': 'constant', 'value': 'missing'}
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(params, f, indent=2)
    
    global _IMPUTATION_PARAMS
    _IMPUTATION_PARAMS = params
    return params

def load_imputation_params(path: str) -> Dict[str, Any]:
    global _IMPUTATION_PARAMS
    with open(path, 'r') as f:
        _IMPUTATION_PARAMS = json.load(f)
    return _IMPUTATION_PARAMS

def apply_imputation(df: pd.DataFrame, params: Dict[str, Any] = None) -> pd.DataFrame:
    """Apply imputation using fitted parameters."""
    if params is None:
        params = _IMPUTATION_PARAMS
    if not params:
        raise ValueError("No imputation parameters. Call fit_imputation_params() first.")
    
    df = df.copy()
    for col, info in params.items():
        if col not in df.columns:
            continue
        if info['type'] == 'median':
            df[col].fillna(info['value'], inplace=True)
        elif info['type'] == 'constant':
            df[col].fillna(info['value'], inplace=True)
        elif info['type'] == 'mode':
            df[col].fillna(info['value'], inplace=True)
    return df

# High-level wrapper
def handle_missing_values(df: pd.DataFrame, mode: str = 'fit', params_path: str = None) -> pd.DataFrame:
    """
    mode: 'fit' - learn and apply imputation (training)
          'transform' - load previously saved params and apply (inference/streaming)
    """
    if mode == 'fit':
        params = fit_imputation_params(df, save_path=params_path)
        return apply_imputation(df, params)
    elif mode == 'transform':
        if params_path is None:
            raise ValueError("params_path required for transform mode")
        params = load_imputation_params(params_path)
        return apply_imputation(df, params)
    else:
        raise ValueError("mode must be 'fit' or 'transform'")