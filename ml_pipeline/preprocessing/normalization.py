# ml_pipeline/preprocessing/normalization.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler
import joblib
import os

def get_scaler(method: str):
    if method == 'robust':
        return RobustScaler()
    elif method == 'standard':
        return StandardScaler()
    elif method == 'minmax':
        return MinMaxScaler()
    else:
        raise ValueError("method must be robust/standard/minmax")

def fit_scaler(df: pd.DataFrame, method: str = 'robust', exclude_cols: list = None,
               save_path: str = None):
    """Fit scaler on numeric columns and save to disk."""
    if exclude_cols is None:
        exclude_cols = ['transaction_id', 'timestamp', 'is_fraud', 'user_id']
    
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns 
                if c not in exclude_cols]
    
    scaler = get_scaler(method)
    scaler.fit(df[num_cols])
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(scaler, save_path)
        # Also save list of columns used
        with open(save_path + '.cols.json', 'w') as f:
            import json
            json.dump(num_cols, f)
    
    return scaler, num_cols

def transform_scaler(df: pd.DataFrame, scaler_path: str, 
                     exclude_cols: list = None) -> pd.DataFrame:
    """Apply pre-fitted scaler to new data."""
    scaler = joblib.load(scaler_path)
    cols_path = scaler_path + '.cols.json'
    with open(cols_path, 'r') as f:
        import json
        num_cols = json.load(f)
    
    # Ensure all required columns exist (if missing, fill with median? but better to raise)
    missing = set(num_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns required for scaling: {missing}")
    
    scaled_values = scaler.transform(df[num_cols])
    scaled_df = pd.DataFrame(scaled_values, columns=num_cols, index=df.index)
    # Replace original columns with scaled versions (or keep both)
    df = df.drop(columns=num_cols)
    df = pd.concat([df, scaled_df], axis=1)
    return df

# Convenience wrapper
def scale_features(df: pd.DataFrame, method: str = 'robust', mode: str = 'fit',
                   scaler_path: str = None, exclude_cols: list = None) -> pd.DataFrame:
    if mode == 'fit':
        fit_scaler(df, method, exclude_cols, scaler_path)
        return transform_scaler(df, scaler_path, exclude_cols)  # apply to same df
    elif mode == 'transform':
        return transform_scaler(df, scaler_path, exclude_cols)
    else:
        raise ValueError("mode must be 'fit' or 'transform'")