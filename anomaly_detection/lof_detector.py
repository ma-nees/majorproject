# anomaly_detection/lof_detector.py
import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from typing import Union, Optional

class LOFDetector:
    """
    Local Outlier Factor detector. Can be fitted on reference data,
    then used to predict on new points (though LOF is transductive).
    We'll use the novelty=True mode to support predict().
    """
    
    def __init__(self, n_neighbors: int = 20, contamination: float = 0.1):
        self.n_neighbors = n_neighbors
        self.contamination = contamination
        self.model = None
    
    def fit(self, X: Union[np.ndarray, pd.DataFrame]):
        """Fit LOF model on reference data."""
        self.model = LocalOutlierFactor(
            n_neighbors=self.n_neighbors,
            contamination=self.contamination,
            novelty=True   # enables predict on new data
        )
        self.model.fit(X)
        return self
    
    def predict_anomaly(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Return 1 for anomaly (fraud), 0 for normal."""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        preds = self.model.predict(X)
        return (preds == -1).astype(int)
    
    def anomaly_score(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Returns negative LOF values (more negative = more anomalous).
        """
        if self.model is None:
            raise ValueError("Model not fitted.")
        # LOF decision_function returns opposite sign: more negative = more outlier
        return self.model.decision_function(X)
    
    def normalized_anomaly_score(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Convert to [0,1] probability-like score."""
        scores = self.anomaly_score(X)
        # Normalize using sigmoid (values typically between -1 and 1)
        normalized = 1 / (1 + np.exp(-scores * 2))
        return normalized
    
    def save(self, path: str):
        joblib.dump(self.model, path)
    
    @classmethod
    def load(cls, path: str, n_neighbors: int = 20, contamination: float = 0.1):
        """Load a pre-fitted LOF model."""
        detector = cls(n_neighbors=n_neighbors, contamination=contamination)
        detector.model = joblib.load(path)
        return detector


def quick_lof_score(reference_data: np.ndarray, new_point: np.ndarray, n_neighbors: int = 20) -> float:
    """
    Quick LOF score for a single new point against reference data.
    Returns normalized anomaly score (0-1).
    """
    detector = LOFDetector(n_neighbors=n_neighbors)
    detector.fit(reference_data)
    score = detector.normalized_anomaly_score(new_point.reshape(1, -1))
    return float(score[0])