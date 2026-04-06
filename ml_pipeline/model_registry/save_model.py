"""
Model Saving Utilities
Handles saving trained models with versioning, metadata, and artifacts (scaler, encoder).
"""

import os
import json
import joblib
import pickle
import hashlib
from datetime import datetime
from typing import Any, Dict, Optional, List
import shutil

class ModelSaver:
    """
    Saves models with automatic versioning and metadata tracking.
    Supports scikit-learn, XGBoost, TensorFlow, and PyTorch models.
    """
    
    def __init__(self, base_dir: str = "models"):
        """
        Initialize model saver.
        
        Args:
            base_dir: Root directory for storing models
        """
        self.base_dir = base_dir
        self.models_dir = os.path.join(base_dir, "models")
        self.metadata_dir = os.path.join(base_dir, "metadata")
        self.artifacts_dir = os.path.join(base_dir, "artifacts")
        
        # Create directories if they don't exist
        for d in [self.models_dir, self.metadata_dir, self.artifacts_dir]:
            os.makedirs(d, exist_ok=True)
    
    def save_model(self, model: Any, model_name: str, 
                   version: Optional[str] = None,
                   metadata: Optional[Dict] = None,
                   artifacts: Optional[Dict[str, Any]] = None,
                   overwrite: bool = False) -> Dict[str, str]:
        """
        Save a trained model with versioning and metadata.
        
        Args:
            model: Trained model object
            model_name: Name of the model (e.g., 'xgboost_fraud')
            version: Version string (if None, auto-increment)
            metadata: Dictionary with training info, metrics, etc.
            artifacts: Additional artifacts (scaler, encoder, feature_names)
            overwrite: If True, overwrite existing version
        
        Returns:
            Dictionary with paths and version info
        """
        # Determine version
        if version is None:
            version = self._get_next_version(model_name)
        
        model_dir = os.path.join(self.models_dir, model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f"{model_name}_v{version}.pkl")
        
        # Check if exists
        if os.path.exists(model_path) and not overwrite:
            raise FileExistsError(f"Model {model_name} v{version} already exists. Use overwrite=True")
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata_dict = {
            "model_name": model_name,
            "version": version,
            "saved_at": datetime.utcnow().isoformat(),
            "model_type": type(model).__name__,
            "file_path": model_path,
            "file_size_mb": os.path.getsize(model_path) / (1024 * 1024),
            "metadata": metadata or {}
        }
        
        metadata_path = os.path.join(self.metadata_dir, f"{model_name}_v{version}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
        
        # Save artifacts
        if artifacts:
            artifact_dir = os.path.join(self.artifacts_dir, f"{model_name}_v{version}")
            os.makedirs(artifact_dir, exist_ok=True)
            for artifact_name, artifact_obj in artifacts.items():
                artifact_path = os.path.join(artifact_dir, f"{artifact_name}.pkl")
                joblib.dump(artifact_obj, artifact_path)
        
        # Update registry index
        self._update_registry(model_name, version, metadata_dict)
        
        return {
            "model_name": model_name,
            "version": version,
            "model_path": model_path,
            "metadata_path": metadata_path,
            "artifact_dir": os.path.join(self.artifacts_dir, f"{model_name}_v{version}") if artifacts else None
        }
    
    def _get_next_version(self, model_name: str) -> str:
        """Get the next version number for a model."""
        model_dir = os.path.join(self.models_dir, model_name)
        if not os.path.exists(model_dir):
            return "1.0.0"
        
        existing_versions = []
        for f in os.listdir(model_dir):
            if f.endswith('.pkl'):
                # Extract version from filename (e.g., xgboost_v1.2.3.pkl)
                parts = f.replace('.pkl', '').split('_v')
                if len(parts) > 1:
                    existing_versions.append(parts[1])
        
        if not existing_versions:
            return "1.0.0"
        
        # Simple increment of patch version
        versions_sorted = sorted(existing_versions, key=lambda v: [int(x) for x in v.split('.')])
        latest = versions_sorted[-1]
        major, minor, patch = map(int, latest.split('.'))
        patch += 1
        return f"{major}.{minor}.{patch}"
    
    def _update_registry(self, model_name: str, version: str, metadata: Dict):
        """Update the model registry index file."""
        registry_path = os.path.join(self.base_dir, "registry.json")
        
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {}
        
        if model_name not in registry:
            registry[model_name] = []
        
        # Add to registry (avoid duplicates)
        existing = [v for v in registry[model_name] if v['version'] == version]
        if not existing:
            registry[model_name].append({
                "version": version,
                "saved_at": metadata['saved_at'],
                "path": metadata['file_path'],
                "metrics": metadata.get('metadata', {}).get('metrics', {})
            })
        
        # Keep only last 10 versions
        registry[model_name] = registry[model_name][-10:]
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def save_ensemble(self, models: Dict[str, Any], ensemble_name: str,
                      weights: Optional[Dict[str, float]] = None,
                      metadata: Optional[Dict] = None) -> Dict:
        """
        Save an ensemble of models.
        
        Args:
            models: Dict mapping model names to model objects
            ensemble_name: Name of the ensemble
            weights: Optional weights for each model
            metadata: Additional metadata
        """
        ensemble_dir = os.path.join(self.models_dir, f"ensemble_{ensemble_name}")
        os.makedirs(ensemble_dir, exist_ok=True)
        
        # Save individual models
        saved_models = {}
        for name, model in models.items():
            model_path = os.path.join(ensemble_dir, f"{name}.pkl")
            joblib.dump(model, model_path)
            saved_models[name] = model_path
        
        # Save ensemble config
        config = {
            "ensemble_name": ensemble_name,
            "models": saved_models,
            "weights": weights or {name: 1.0/len(models) for name in models},
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        config_path = os.path.join(ensemble_dir, "ensemble_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "ensemble_name": ensemble_name,
            "config_path": config_path,
            "model_count": len(models)
        }

# Convenience function
def save_fraud_model(model: Any, model_name: str, 
                     metrics: Dict[str, float],
                     scaler: Any = None,
                     encoder: Any = None,
                     feature_names: Optional[List[str]] = None,
                     version: Optional[str] = None) -> Dict:
    """
    Convenience function to save a fraud detection model with common artifacts.
    """
    saver = ModelSaver()
    
    artifacts = {}
    if scaler is not None:
        artifacts['scaler'] = scaler
    if encoder is not None:
        artifacts['encoder'] = encoder
    if feature_names is not None:
        artifacts['feature_names'] = feature_names
    
    metadata = {
        "metrics": metrics,
        "feature_count": len(feature_names) if feature_names else None,
        "purpose": "fraud_detection"
    }
    
    return saver.save_model(model, model_name, version=version, 
                            metadata=metadata, artifacts=artifacts)

if __name__ == "__main__":
    # Example
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    saver = ModelSaver()
    result = saver.save_model(model, "test_model", metadata={"test": True})
    print("Saved model:", result)