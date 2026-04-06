"""
Confusion Matrix Utilities
Generates and visualizes confusion matrices for fraud detection models.
Supports matplotlib and plotly visualizations.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix as sk_cm
from typing import Dict, List, Optional, Tuple, Union
import warnings

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("Matplotlib/seaborn not available. Install for visualizations.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

class ConfusionMatrixAnalyzer:
    """
    Comprehensive confusion matrix analysis and visualization.
    Includes normalized matrices, derived metrics, and multiple plotting options.
    """
    
    def __init__(self, labels: List[str] = None):
        """
        Initialize analyzer.
        
        Args:
            labels: Class labels, default ['Legitimate', 'Fraud']
        """
        self.labels = labels or ['Legitimate', 'Fraud']
    
    def compute_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, 
                       normalize: Optional[str] = None) -> np.ndarray:
        """
        Compute confusion matrix.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            normalize: None, 'true', 'pred', or 'all'
        
        Returns:
            Confusion matrix as numpy array
        """
        cm = sk_cm(y_true, y_pred)
        
        if normalize == 'true':
            cm = cm.astype('float') / cm.sum(axis=1, keepdims=True)
        elif normalize == 'pred':
            cm = cm.astype('float') / cm.sum(axis=0, keepdims=True)
        elif normalize == 'all':
            cm = cm.astype('float') / cm.sum()
        
        return cm
    
    def extract_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Extract all metrics from confusion matrix.
        
        Returns:
            Dictionary with TN, FP, FN, TP and derived metrics
        """
        tn, fp, fn, tp = sk_cm(y_true, y_pred).ravel()
        
        metrics = {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'total_samples': int(tn + fp + fn + tp),
            'accuracy': (tp + tn) / (tn + fp + fn + tp) if (tn + fp + fn + tp) > 0 else 0,
            'precision': tp / (tp + fp) if (tp + fp) > 0 else 0,
            'recall': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
        }
        return metrics
    
    def plot_matplotlib(self, y_true: np.ndarray, y_pred: np.ndarray,
                        normalize: Optional[str] = None,
                        title: str = "Confusion Matrix",
                        figsize: Tuple[int, int] = (8, 6),
                        cmap: str = 'Blues',
                        save_path: Optional[str] = None):
        """
        Plot confusion matrix using matplotlib/seaborn.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            normalize: None, 'true', 'pred', 'all'
            title: Plot title
            figsize: Figure size
            cmap: Colormap
            save_path: If provided, save figure to path
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib and seaborn are required for this plot")
        
        cm = self.compute_matrix(y_true, y_pred, normalize)
        
        # Determine format for annotations
        if normalize:
            fmt = '.3f'
            annot = np.around(cm, 3)
        else:
            fmt = 'd'
            annot = cm.astype(int)
        
        plt.figure(figsize=figsize)
        sns.heatmap(cm, annot=annot, fmt=fmt, cmap=cmap, 
                    xticklabels=self.labels, yticklabels=self.labels,
                    cbar=True, square=True)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
    
    def plot_plotly(self, y_true: np.ndarray, y_pred: np.ndarray,
                    normalize: Optional[str] = None,
                    title: str = "Confusion Matrix"):
        """
        Plot interactive confusion matrix using plotly.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            normalize: None, 'true', 'pred', 'all'
            title: Plot title
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("plotly is required for this plot")
        
        cm = self.compute_matrix(y_true, y_pred, normalize)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=self.labels,
            y=self.labels,
            text=[[f"{val:.4f}" if normalize else f"{int(val)}" for val in row] for row in cm],
            texttemplate="%{text}",
            textfont={"size": 12},
            colorscale='Blues',
            showscale=True,
            zmin=0,
            zmax=1 if normalize else None
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Predicted Label",
            yaxis_title="True Label",
            width=600,
            height=500,
            font=dict(size=12)
        )
        
        fig.show()
        return fig
    
    def print_table(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Print confusion matrix as formatted table."""
        cm = self.compute_matrix(y_true, y_pred)
        metrics = self.extract_metrics(y_true, y_pred)
        
        print("\n" + "=" * 40)
        print("CONFUSION MATRIX")
        print("=" * 40)
        print(f"{'':15} Predicted")
        print(f"{'':12} {self.labels[0]:>10} {self.labels[1]:>10}")
        print(f"{self.labels[0]:<12} {cm[0][0]:>10} {cm[0][1]:>10}")
        print(f"{self.labels[1]:<12} {cm[1][0]:>10} {cm[1][1]:>10}")
        
        print("\n" + "-" * 40)
        print("DERIVED METRICS")
        print("-" * 40)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').title():20}: {value:.4f}")
            else:
                print(f"{key.replace('_', ' ').title():20}: {value}")
        print("=" * 40 + "\n")

# Helper functions for quick analysis
def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, 
                          labels: List[str] = None,
                          normalize: Optional[str] = None,
                          interactive: bool = False):
    """
    Quick plot of confusion matrix (matplotlib or plotly).
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        labels: Class labels
        normalize: None, 'true', 'pred', 'all'
        interactive: Use plotly interactive plot if True
    """
    analyzer = ConfusionMatrixAnalyzer(labels)
    if interactive and PLOTLY_AVAILABLE:
        analyzer.plot_plotly(y_true, y_pred, normalize)
    else:
        analyzer.plot_matplotlib(y_true, y_pred, normalize)

def get_confusion_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Quickly get metrics from confusion matrix."""
    analyzer = ConfusionMatrixAnalyzer()
    return analyzer.extract_metrics(y_true, y_pred)

if __name__ == "__main__":
    # Example
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 0])
    
    analyzer = ConfusionMatrixAnalyzer()
    analyzer.print_table(y_true, y_pred)
    
    # Plot if matplotlib is available
    if MATPLOTLIB_AVAILABLE:
        analyzer.plot_matplotlib(y_true, y_pred, title="Fraud Detection Confusion Matrix")