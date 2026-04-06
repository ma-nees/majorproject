"""
Model Evaluation Metrics
Provides comprehensive metrics for fraud detection models including precision, recall, F1, AUC-ROC, and business-specific metrics.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, matthews_corrcoef, cohen_kappa_score,
    log_loss, brier_score_loss
)
from typing import Dict, List, Optional, Tuple, Union
import warnings

class FraudMetrics:
    """
    Comprehensive metrics calculator for fraud detection models.
    Includes standard ML metrics and fraud-specific metrics (cost savings, false positive rate, etc.)
    """
    
    def __init__(self, fraud_cost: float = 100.0, review_cost: float = 5.0):
        """
        Initialize with business costs for fraud detection.
        
        Args:
            fraud_cost: Cost of a missed fraud (false negative)
            review_cost: Cost of investigating a false positive
        """
        self.fraud_cost = fraud_cost
        self.review_cost = review_cost
    
    def calculate_all_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                              y_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Calculate all standard classification metrics.
        
        Args:
            y_true: Ground truth labels (0 = legitimate, 1 = fraud)
            y_pred: Predicted labels
            y_proba: Predicted probabilities (for AUC, log loss)
        
        Returns:
            Dictionary with all metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
        metrics['f1_score'] = f1_score(y_true, y_pred, zero_division=0)
        metrics['specificity'] = self._calculate_specificity(y_true, y_pred)
        metrics['false_positive_rate'] = 1 - metrics['specificity']
        metrics['false_negative_rate'] = 1 - metrics['recall']
        
        # Advanced metrics
        metrics['matthews_corrcoef'] = matthews_corrcoef(y_true, y_pred)
        metrics['cohen_kappa'] = cohen_kappa_score(y_true, y_pred)
        
        # Probability-based metrics
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            metrics['pr_auc'] = average_precision_score(y_true, y_proba)
            metrics['log_loss'] = log_loss(y_true, y_proba)
            metrics['brier_score'] = brier_score_loss(y_true, y_proba)
        
        # Business metrics
        metrics['fraud_detection_rate'] = metrics['recall']  # alias
        metrics['false_positive_rate_business'] = metrics['false_positive_rate']
        metrics['cost_savings'] = self._calculate_cost_savings(y_true, y_pred)
        metrics['cost_per_transaction'] = self._calculate_cost_per_transaction(y_true, y_pred)
        
        return metrics
    
    def _calculate_specificity(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate specificity (true negative rate)."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return tn / (tn + fp) if (tn + fp) > 0 else 0
    
    def _calculate_cost_savings(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate estimated cost savings compared to no model.
        
        Assumptions:
        - No model: all frauds cause loss, no review costs
        - With model: detected frauds are blocked (saved), false positives incur review cost
        """
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        # Cost without model: all frauds cause loss
        total_frauds = tp + fn
        cost_no_model = total_frauds * self.fraud_cost
        
        # Cost with model: missed frauds cause loss + false positives incur review cost
        cost_with_model = fn * self.fraud_cost + fp * self.review_cost
        
        savings = cost_no_model - cost_with_model
        return max(savings, 0)
    
    def _calculate_cost_per_transaction(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate average cost per transaction when using the model."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        total_transactions = tn + fp + fn + tp
        total_cost = fn * self.fraud_cost + fp * self.review_cost
        return total_cost / total_transactions if total_transactions > 0 else 0
    
    def get_metrics_at_threshold(self, y_true: np.ndarray, y_proba: np.ndarray, 
                                  threshold: float) -> Dict[str, float]:
        """
        Calculate metrics at a specific probability threshold.
        
        Args:
            y_true: Ground truth labels
            y_proba: Predicted probabilities
            threshold: Decision threshold (0 to 1)
        """
        y_pred = (y_proba >= threshold).astype(int)
        return self.calculate_all_metrics(y_true, y_pred, y_proba)
    
    def find_optimal_threshold(self, y_true: np.ndarray, y_proba: np.ndarray,
                               metric: str = 'f1_score') -> Tuple[float, Dict]:
        """
        Find the optimal probability threshold to maximize a given metric.
        
        Args:
            y_true: Ground truth labels
            y_proba: Predicted probabilities
            metric: Metric to optimize ('f1_score', 'precision', 'recall', 'cost_savings')
        
        Returns:
            Tuple of (best_threshold, best_metrics)
        """
        thresholds = np.linspace(0.01, 0.99, 50)
        best_score = -1
        best_threshold = 0.5
        best_metrics = {}
        
        for thresh in thresholds:
            metrics = self.get_metrics_at_threshold(y_true, y_proba, thresh)
            score = metrics.get(metric, 0)
            if score > best_score:
                best_score = score
                best_threshold = thresh
                best_metrics = metrics
        
        return best_threshold, best_metrics
    
    def generate_report(self, y_true: np.ndarray, y_pred: np.ndarray,
                        y_proba: Optional[np.ndarray] = None) -> str:
        """Generate a human-readable evaluation report."""
        metrics = self.calculate_all_metrics(y_true, y_pred, y_proba)
        
        report = []
        report.append("=" * 50)
        report.append("FRAUD DETECTION MODEL EVALUATION REPORT")
        report.append("=" * 50)
        report.append(f"\nPerformance Metrics:")
        report.append(f"  Accuracy:          {metrics['accuracy']:.4f}")
        report.append(f"  Precision:         {metrics['precision']:.4f}")
        report.append(f"  Recall (Detection):{metrics['recall']:.4f}")
        report.append(f"  F1 Score:          {metrics['f1_score']:.4f}")
        report.append(f"  Specificity:       {metrics['specificity']:.4f}")
        report.append(f"  False Positive Rate: {metrics['false_positive_rate']:.4f}")
        
        if y_proba is not None:
            report.append(f"\nProbability Metrics:")
            report.append(f"  ROC-AUC:           {metrics['roc_auc']:.4f}")
            report.append(f"  PR-AUC:            {metrics['pr_auc']:.4f}")
        
        report.append(f"\nBusiness Impact:")
        report.append(f"  Estimated Cost Savings: ${metrics['cost_savings']:,.2f}")
        report.append(f"  Cost per Transaction:   ${metrics['cost_per_transaction']:.4f}")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)

# Standalone functions for quick use
def quick_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> Dict:
    """Quick metrics calculation using default settings."""
    evaluator = FraudMetrics()
    return evaluator.calculate_all_metrics(y_true, y_pred, y_proba)

def classification_metrics_report(y_true: np.ndarray, y_pred: np.ndarray) -> str:
    """Return sklearn's classification report as string."""
    return classification_report(y_true, y_pred, target_names=['Legitimate', 'Fraud'])

if __name__ == "__main__":
    # Example usage
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 0])
    y_proba = np.array([0.1, 0.2, 0.9, 0.4, 0.3, 0.8, 0.2, 0.6, 0.95, 0.1])
    
    evaluator = FraudMetrics()
    metrics = evaluator.calculate_all_metrics(y_true, y_pred, y_proba)
    print(evaluator.generate_report(y_true, y_pred, y_proba))