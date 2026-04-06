"""
LIME (Local Interpretable Model-agnostic Explanations) Explainer
Provides local explanations for individual fraud predictions.
Model-agnostic, works with any classifier.
"""

import numpy as np
import pandas as pd
import lime
import lime.lime_tabular
import joblib
import os
from typing import Dict, List, Any, Optional, Callable

class LIMEExplainer:
    def __init__(self, model_path: str = "models/xgboost_fraud_model.pkl",
                 training_data: Optional[np.ndarray] = None,
                 feature_names: Optional[List[str]] = None,
                 class_names: Optional[List[str]] = None):
        """
        Initialize LIME explainer with a trained model and training data.
        
        Args:
            model_path: Path to the saved model
            training_data: Background training data (required for LIME)
            feature_names: List of feature names
            class_names: List of class names (e.g., ["legitimate", "fraud"])
        """
        self.model = self._load_model(model_path)
        self.feature_names = feature_names or [f"feature_{i}" for i in range(10)]
        self.class_names = class_names or ["legitimate", "fraud"]
        
        if training_data is None:
            # Generate dummy training data if not provided (not ideal)
            training_data = np.random.randn(100, len(self.feature_names))
        
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data,
            feature_names=self.feature_names,
            class_names=self.class_names,
            mode='classification',
            discretize_continuous=True,
            random_state=42
        )
    
    def _load_model(self, model_path: str):
        """Load the trained model."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        return joblib.load(model_path)
    
    def _predict_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Wrapper for model prediction (LIME expects this signature).
        Returns probability for each class.
        """
        return self.model.predict_proba(features)
    
    def explain_prediction(self, features: np.ndarray, num_features: int = 5,
                           num_samples: int = 5000) -> Dict[str, Any]:
        """
        Generate LIME explanation for a single prediction.
        
        Args:
            features: Single sample feature vector (1D array)
            num_features: Number of top features to show
            num_samples: Number of samples for LIME perturbation
        
        Returns:
            Dictionary with explanation details
        """
        if len(features.shape) > 1:
            features = features.flatten()
        
        # Get prediction probability
        proba = self.model.predict_proba(features.reshape(1, -1))[0][1]
        
        # Generate LIME explanation
        explanation = self.explainer.explain_instance(
            features, 
            self._predict_proba,
            num_features=num_features,
            num_samples=num_samples
        )
        
        # Extract feature contributions
        contributions = []
        for feature, weight in explanation.as_list():
            contributions.append({
                "feature": feature,
                "weight": float(weight),
                "impact": "positive" if weight > 0 else "negative",
                "abs_weight": abs(float(weight))
            })
        
        contributions.sort(key=lambda x: x["abs_weight"], reverse=True)
        
        # Get feature values
        feature_values = []
        for i, name in enumerate(self.feature_names):
            if i < len(features):
                feature_values.append({
                    "feature": name,
                    "value": float(features[i])
                })
        
        return {
            "fraud_probability": float(proba),
            "top_features": contributions[:num_features],
            "feature_values": feature_values,
            "explanation_map": explanation.as_map(),
            "explanation_html": explanation.as_html() if hasattr(explanation, 'as_html') else None
        }
    
    def explain_prediction_with_custom_weights(self, features: np.ndarray,
                                               feature_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Generate explanation with custom feature importance weights.
        
        Args:
            features: Single sample feature vector
            feature_weights: Dictionary mapping feature names to custom weights
        
        Returns:
            Explanation with weighted contributions
        """
        explanation = self.explain_prediction(features)
        
        if feature_weights:
            for contrib in explanation["top_features"]:
                feat_name = contrib["feature"].split("=")[0]  # LIME may include value
                if feat_name in feature_weights:
                    contrib["custom_weight"] = feature_weights[feat_name]
                    contrib["weighted_impact"] = contrib["weight"] * feature_weights[feat_name]
        
        return explanation
    
    def compare_explanations(self, features1: np.ndarray, features2: np.ndarray) -> Dict[str, Any]:
        """
        Compare explanations for two different samples (e.g., fraud vs legitimate).
        
        Returns:
            Dictionary with both explanations and comparison metrics
        """
        exp1 = self.explain_prediction(features1)
        exp2 = self.explain_prediction(features2)
        
        # Find common features and compare weights
        common_features = {}
        for c1 in exp1["top_features"]:
            for c2 in exp2["top_features"]:
                if c1["feature"] == c2["feature"]:
                    common_features[c1["feature"]] = {
                        "sample1_weight": c1["weight"],
                        "sample2_weight": c2["weight"],
                        "difference": c1["weight"] - c2["weight"]
                    }
        
        return {
            "sample1": exp1,
            "sample2": exp2,
            "common_features": common_features,
            "similarity_score": 1 - abs(exp1["fraud_probability"] - exp2["fraud_probability"])
        }

# Singleton instance
_lime_explainer_instance = None

def get_lime_explainer(model_path: str = "models/xgboost_fraud_model.pkl",
                       training_data: Optional[np.ndarray] = None,
                       feature_names: Optional[List[str]] = None) -> LIMEExplainer:
    """Get or create LIME explainer singleton."""
    global _lime_explainer_instance
    if _lime_explainer_instance is None:
        _lime_explainer_instance = LIMEExplainer(model_path, training_data, feature_names)
    return _lime_explainer_instance