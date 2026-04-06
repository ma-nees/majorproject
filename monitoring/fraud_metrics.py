# monitoring/fraud_metrics.py
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml_pipeline.evaluation.metrics import FraudMetrics

class FraudMetricsTracker:
    """
    Tracks fraud detection metrics over time.
    Stores per-batch metrics and cumulative metrics.
    Can detect model performance degradation.
    """
    
    def __init__(self, storage_dir: str = "monitoring/data", 
                 fraud_cost: float = 100.0, review_cost: float = 5.0):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.storage_dir / "fraud_metrics_history.csv"
        self.predictions_file = self.storage_dir / "predictions_log.csv"
        self.fraud_metrics = FraudMetrics(fraud_cost, review_cost)
        
    def log_batch(self, y_true: np.ndarray, y_pred: np.ndarray, 
                  y_proba: Optional[np.ndarray] = None,
                  model_name: str = "unknown",
                  batch_id: Optional[str] = None) -> Dict:
        """
        Log metrics for a batch of predictions.
        Returns the computed metrics.
        """
        metrics = self.fraud_metrics.calculate_all_metrics(y_true, y_pred, y_proba)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "batch_id": batch_id or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "n_samples": len(y_true),
            "n_fraud_true": int(np.sum(y_true)),
            "n_fraud_pred": int(np.sum(y_pred)),
        }
        record.update(metrics)
        
        # Append to CSV
        df_new = pd.DataFrame([record])
        if self.metrics_file.exists():
            df_existing = pd.read_csv(self.metrics_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        df_combined.to_csv(self.metrics_file, index=False)
        
        return metrics
    
    def log_prediction(self, transaction_id: str, model_name: str,
                       true_label: Optional[int], pred_label: int,
                       proba: float, additional_features: Dict = None):
        """
        Log each transaction prediction for later analysis.
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "model_name": model_name,
            "true_label": true_label,
            "pred_label": pred_label,
            "probability": proba
        }
        if additional_features:
            record.update(additional_features)
        
        df_new = pd.DataFrame([record])
        if self.predictions_file.exists():
            df_existing = pd.read_csv(self.predictions_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        df_combined.to_csv(self.predictions_file, index=False)
    
    def get_recent_metrics(self, hours: int = 24) -> pd.DataFrame:
        """Return metrics from the last N hours."""
        if not self.metrics_file.exists():
            return pd.DataFrame()
        df = pd.read_csv(self.metrics_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = datetime.now() - pd.Timedelta(hours=hours)
        return df[df['timestamp'] >= cutoff]
    
    def detect_performance_drop(self, metric: str = 'recall', 
                                threshold_drop: float = 0.05,
                                window_hours: int = 24) -> bool:
        """
        Detect if recent performance has dropped significantly compared to baseline.
        Returns True if drop > threshold_drop.
        """
        df = self.get_recent_metrics(hours=window_hours)
        if len(df) < 2:
            return False
        
        # Baseline: average of first 50% of window
        baseline = df.head(len(df)//2)[metric].mean()
        # Recent: average of last 25% of window
        recent = df.tail(len(df)//4)[metric].mean()
        
        return (baseline - recent) > threshold_drop
    
    def generate_performance_report(self) -> str:
        """Generate a text report of recent model performance."""
        df = self.get_recent_metrics(hours=168)  # last 7 days
        if df.empty:
            return "No metrics logged yet."
        
        latest = df.iloc[-1]
        report = []
        report.append("=" * 60)
        report.append("FRAUD DETECTION PERFORMANCE REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 60)
        report.append(f"\nLatest Batch ({latest['batch_id']}):")
        report.append(f"  Model: {latest['model_name']}")
        report.append(f"  Recall: {latest['recall']:.4f}")
        report.append(f"  Precision: {latest['precision']:.4f}")
        report.append(f"  F1: {latest['f1_score']:.4f}")
        report.append(f"  ROC-AUC: {latest.get('roc_auc', 0):.4f}")
        report.append(f"  Cost Savings: ${latest.get('cost_savings', 0):,.2f}")
        
        # Trend
        if len(df) >= 5:
            recall_trend = df['recall'].rolling(5).mean()
            report.append(f"\nTrend (5-batch avg recall): {recall_trend.iloc[-1]:.4f} (from {recall_trend.iloc[0]:.4f})")
        
        return "\n".join(report)


# Singleton for easy import
_tracker_instance = None

def get_metrics_tracker() -> FraudMetricsTracker:
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = FraudMetricsTracker()
    return _tracker_instance