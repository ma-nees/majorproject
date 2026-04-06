# anomaly_detection/isolation_forest_detector.py
import joblib
import numpy as np
import pandas as pd
from typing import Union, Optional, Dict, Any

class IsolationForestDetector:
    """
    Wrapper for pre-trained Isolation Forest model.
    Provides anomaly scoring for single transactions or batches.
    """
    
    def __init__(self, model_path: str):
        """
        Args:
            model_path: Path to saved Isolation Forest model (.pkl)
        """
        self.model = joblib.load(model_path)
        self.is_fitted = True
    
    def predict_anomaly(self, features: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Returns binary predictions: 1 for anomaly (fraud), 0 for normal.
        """
        preds = self.model.predict(features)
        return (preds == -1).astype(int)
    
    def anomaly_score(self, features: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Returns anomaly score: more negative = more anomalous.
        For convenience, we also return a normalized [0,1] score where higher = more anomalous.
        """
        scores = self.model.decision_function(features)  # range approx [-0.5, 0.5]
        return scores
    
    def normalized_anomaly_score(self, features: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Returns anomaly probability-like score in [0,1] (higher = more anomalous).
        Uses sigmoid scaling (not true probability but useful for ranking).
        """
        scores = self.anomaly_score(features)
        # Shift and scale: typical Isolation Forest decision_function output ~ [-0.5, 0.5]
        # Normalize to [0,1] where 0 is normal, 1 is anomalous
        normalized = 1 / (1 + np.exp(-scores * 5))  # sigmoid with steepness factor
        return normalized
    
    def get_risk_score(self, features: Union[np.ndarray, pd.DataFrame]) -> float:
        """
        Returns a risk score (0-100) for a single transaction.
        """
        score = self.normalized_anomaly_score(features)
        if isinstance(score, np.ndarray):
            score = score[0] if len(score) > 0 else 0
        return float(score * 100)
    
    def batch_predict(self, df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
        """
        Add anomaly predictions and scores to a DataFrame.
        """
        X = df[feature_columns].values
        df = df.copy()
        df['if_anomaly'] = self.predict_anomaly(X)
        df['if_anomaly_score'] = self.anomaly_score(X)
        df['if_risk_score'] = self.normalized_anomaly_score(X) * 100
        return df


# Standalone function for quick scoring
def load_if_detector(model_path: str) -> IsolationForestDetector:
    return IsolationForestDetector(model_path)