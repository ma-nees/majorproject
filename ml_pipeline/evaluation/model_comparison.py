"""
Model Comparison Utilities
Compares multiple fraud detection models (Logistic Regression, Random Forest, XGBoost, Isolation Forest)
and generates comparison tables and visualizations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.model_selection import cross_val_score, StratifiedKFold
import warnings

class ModelComparator:
    """
    Compare multiple models using cross-validation and test set evaluation.
    Supports standard classifiers and anomaly detectors.
    """
    
    def __init__(self, models: Dict[str, Any], cv_folds: int = 5, scoring: str = 'roc_auc'):
        """
        Initialize comparator with models.
        
        Args:
            models: Dictionary mapping model names to sklearn-like estimator instances
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric for cross-validation
        """
        self.models = models
        self.cv_folds = cv_folds
        self.scoring = scoring
        self.cv_results = {}
        self.test_results = {}
    
    def cross_validate(self, X: np.ndarray, y: np.ndarray) -> pd.DataFrame:
        """
        Perform cross-validation for all models.
        
        Args:
            X: Feature matrix
            y: Target labels
        
        Returns:
            DataFrame with cross-validation results
        """
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        
        results = []
        for name, model in self.models.items():
            try:
                scores = cross_val_score(model, X, y, cv=cv, scoring=self.scoring)
                self.cv_results[name] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
                results.append({
                    'Model': name,
                    f'Mean {self.scoring}': f"{scores.mean():.4f}",
                    f'Std {self.scoring}': f"{scores.std():.4f}",
                    'Fit Time': 'N/A'  # Could add timing
                })
            except Exception as e:
                warnings.warn(f"Cross-validation failed for {name}: {e}")
                results.append({
                    'Model': name,
                    f'Mean {self.scoring}': 'Error',
                    f'Std {self.scoring}': 'Error',
                    'Fit Time': 'N/A'
                })
        
        return pd.DataFrame(results)
    
    def evaluate_on_test(self, X_train: np.ndarray, y_train: np.ndarray,
                         X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """
        Train on training set and evaluate on test set.
        
        Returns:
            DataFrame with test set metrics
        """
        from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
        
        results = []
        for name, model in self.models.items():
            try:
                # Train
                model.fit(X_train, y_train)
                
                # Predict probabilities and labels
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)[:, 1]
                else:
                    y_proba = model.decision_function(X_test) if hasattr(model, 'decision_function') else None
                
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                metrics = {
                    'Model': name,
                    'Accuracy': accuracy_score(y_test, y_pred),
                    'Precision': precision_score(y_test, y_pred, zero_division=0),
                    'Recall': recall_score(y_test, y_pred, zero_division=0),
                    'F1 Score': f1_score(y_test, y_pred, zero_division=0),
                }
                
                if y_proba is not None:
                    metrics['ROC-AUC'] = roc_auc_score(y_test, y_proba)
                
                results.append(metrics)
                self.test_results[name] = metrics
                
            except Exception as e:
                warnings.warn(f"Test evaluation failed for {name}: {e}")
                results.append({'Model': name, 'Error': str(e)})
        
        return pd.DataFrame(results)
    
    def get_best_model(self, metric: str = 'roc_auc') -> Tuple[str, Dict]:
        """
        Identify the best performing model based on test metric.
        
        Args:
            metric: Metric to compare (e.g., 'roc_auc', 'f1_score')
        
        Returns:
            Tuple of (best_model_name, best_metrics)
        """
        best_name = None
        best_score = -1
        best_metrics = {}
        
        for name, metrics in self.test_results.items():
            score = metrics.get(metric, -1)
            if score > best_score:
                best_score = score
                best_name = name
                best_metrics = metrics
        
        return best_name, best_metrics
    
    def generate_comparison_report(self) -> str:
        """Generate a text report comparing all models."""
        report = []
        report.append("=" * 60)
        report.append("MODEL COMPARISON REPORT")
        report.append("=" * 60)
        
        if self.test_results:
            report.append("\nTest Set Performance:")
            report.append("-" * 40)
            df = pd.DataFrame(self.test_results).T
            report.append(df.to_string())
        
        if self.cv_results:
            report.append("\nCross-Validation Performance:")
            report.append("-" * 40)
            for name, res in self.cv_results.items():
                report.append(f"{name}: {self.scoring} = {res['mean']:.4f} (+/- {res['std']:.4f})")
        
        best_name, best_metrics = self.get_best_model()
        report.append(f"\nBest Model: {best_name}")
        report.append(f"  ROC-AUC: {best_metrics.get('roc_auc', 'N/A'):.4f}")
        report.append(f"  F1 Score: {best_metrics.get('f1_score', 'N/A'):.4f}")
        
        return "\n".join(report)

# Additional utilities for comparing multiple runs
def compare_models_across_datasets(model_results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Compare model performance across multiple datasets or folds.
    
    Args:
        model_results: Nested dict {model_name: {metric_name: value, ...}}
    
    Returns:
        DataFrame with model rankings
    """
    df = pd.DataFrame(model_results).T
    return df

def rank_models_by_metric(metrics_dict: Dict[str, float], higher_is_better: bool = True) -> List[Tuple[str, float]]:
    """Rank models by a specific metric."""
    sorted_items = sorted(metrics_dict.items(), key=lambda x: x[1], reverse=higher_is_better)
    return sorted_items

# Helper imports
from sklearn.metrics import accuracy_score

if __name__ == "__main__":
    # Example usage with dummy data
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    import xgboost as xgb
    
    # Generate dummy data
    X = np.random.randn(1000, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    X_train, X_test = X[:800], X[800:]
    y_train, y_test = y[:800], y[800:]
    
    models = {
        'Logistic Regression': LogisticRegression(),
        'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42),
        'XGBoost': xgb.XGBClassifier(n_estimators=50, random_state=42)
    }
    
    comparator = ModelComparator(models)
    cv_results = comparator.cross_validate(X_train, y_train)
    test_results = comparator.evaluate_on_test(X_train, y_train, X_test, y_test)
    print(comparator.generate_comparison_report())