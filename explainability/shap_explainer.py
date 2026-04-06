"""
SHAP (SHapley Additive exPlanations) Explainer
Provides global feature importance and local explanations for fraud predictions.
Supports tree-based models (XGBoost, RandomForest) and linear models.
"""

import shap
import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, List, Any, Optional, Union

class SHAPExplainer:
    def __init__(self, model_path: str = "models/xgboost_fraud_model.pkl", 
                 feature_names: Optional[List[str]] = None):
        """
        Initialize SHAP explainer with a trained model.
        
        Args:
            model_path: Path to the saved model (.pkl)
            feature_names: List of feature names (for display)
        """
        self.model = self._load_model(model_path)
        self.feature_names = feature_names
        self.explainer = None
        self._initialize_explainer()
    
    def _load_model(self, model_path: str):
        """Load the trained model."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        return joblib.load(model_path)
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer based on model type."""
        try:
            # Tree-based models (XGBoost, RandomForest, LightGBM)
            self.explainer = shap.TreeExplainer(self.model)
        except Exception:
            try:
                # Linear models
                self.explainer = shap.LinearExplainer(self.model)
            except Exception:
                # Fallback to KernelExplainer (slower but model-agnostic)
                self.explainer = shap.KernelExplainer(self.model.predict_proba, np.zeros((1, 1)))
    
    def explain_prediction(self, features: np.ndarray, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate local explanation for a single prediction.
        
        Args:
            features: Single sample feature vector (1D array or 2D with 1 row)
            feature_names: Optional feature names for the output
        
        Returns:
            Dictionary with SHAP values, base value, and feature contributions
        """
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        shap_values = self.explainer.shap_values(features)
        
        # For binary classification, shap_values shape may be (n_samples, n_features) or list of arrays
        if isinstance(shap_values, list):
            # For models that return separate arrays for each class
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        elif len(shap_values.shape) == 3:
            shap_values = shap_values[:, :, 1]  # take positive class
        
        shap_values_sample = shap_values[0]
        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[1] if len(base_value) > 1 else base_value[0]
        
        # Build feature contributions
        contributions = []
        names = feature_names or self.feature_names or [f"feature_{i}" for i in range(len(shap_values_sample))]
        
        for i, (name, shap_val) in enumerate(zip(names, shap_values_sample)):
            contributions.append({
                "feature": name,
                "shap_value": float(shap_val),
                "impact": "positive" if shap_val > 0 else "negative",
                "abs_impact": abs(float(shap_val))
            })
        
        # Sort by absolute impact
        contributions.sort(key=lambda x: x["abs_impact"], reverse=True)
        
        # Prediction probability (fraud probability)
        proba = self.model.predict_proba(features)[0][1]
        
        return {
            "fraud_probability": float(proba),
            "base_value": float(base_value),
            "shap_values": contributions,
            "explanation_summary": self._summarize_explanation(contributions)
        }
    
    def global_feature_importance(self, background_data: np.ndarray, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compute global feature importance using SHAP.
        
        Args:
            background_data: Sample of training data (for KernelExplainer) or full dataset
            feature_names: Optional feature names
        
        Returns:
            Dictionary with feature importance scores (mean |SHAP|)
        """
        shap_values = self.explainer.shap_values(background_data)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        elif len(shap_values.shape) == 3:
            shap_values = shap_values[:, :, 1]
        
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        names = feature_names or self.feature_names or [f"feature_{i}" for i in range(len(mean_abs_shap))]
        
        importance = []
        for name, score in zip(names, mean_abs_shap):
            importance.append({
                "feature": name,
                "importance": float(score)
            })
        
        importance.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "feature_importance": importance,
            "total_features": len(importance)
        }
    
    def _summarize_explanation(self, contributions: List[Dict]) -> str:
        """Generate a human-readable summary of the explanation."""
        top_positive = [c for c in contributions if c["impact"] == "positive"][:3]
        top_negative = [c for c in contributions if c["impact"] == "negative"][:3]
        
        summary_parts = []
        if top_positive:
            pos_str = ", ".join([f"{c['feature']} (+{c['shap_value']:.3f})" for c in top_positive])
            summary_parts.append(f"Increased risk: {pos_str}")
        if top_negative:
            neg_str = ", ".join([f"{c['feature']} ({c['shap_value']:.3f})" for c in top_negative])
            summary_parts.append(f"Decreased risk: {neg_str}")
        
        return " | ".join(summary_parts) if summary_parts else "No significant features"

# Singleton instance for reuse
_shap_explainer_instance = None

def get_shap_explainer(model_path: str = "models/xgboost_fraud_model.pkl",
                       feature_names: Optional[List[str]] = None) -> SHAPExplainer:
    """Get or create SHAP explainer singleton."""
    global _shap_explainer_instance
    if _shap_explainer_instance is None:
        _shap_explainer_instance = SHAPExplainer(model_path, feature_names)
    return _shap_explainer_instance