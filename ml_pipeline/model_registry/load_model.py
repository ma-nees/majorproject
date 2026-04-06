"""
Model Loading Utilities
Loads trained models from registry with version control and artifact loading.
"""

import os
import json
import joblib
from typing import Any, Dict, Optional, Tuple, List

class ModelLoader:
    """
    Loads models from the registry with version management.
    Supports loading latest, specific version, or production models.
    """
    
    def __init__(self, base_dir: str = "models"):
        """
        Initialize model loader.
        
        Args:
            base_dir: Root directory where models are stored
        """
        self.base_dir = base_dir
        self.models_dir = os.path.join(base_dir, "models")
        self.metadata_dir = os.path.join(base_dir, "metadata")
        self.artifacts_dir = os.path.join(base_dir, "artifacts")
        self.registry_path = os.path.join(base_dir, "registry.json")
    
    def load_model(self, model_name: str, version: Optional[str] = None,
                   load_artifacts: bool = False) -> Tuple[Any, Optional[Dict]]:
        """
        Load a model by name and optional version.
        
        Args:
            model_name: Name of the model (e.g., 'xgboost_fraud')
            version: Version string (if None, loads latest)
            load_artifacts: If True, also load associated artifacts
        
        Returns:
            Tuple of (model, artifacts_dict)
        """
        if version is None:
            version = self._get_latest_version(model_name)
            if version is None:
                raise FileNotFoundError(f"No model found for {model_name}")
        
        model_path = os.path.join(self.models_dir, model_name, f"{model_name}_v{version}.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        model = joblib.load(model_path)
        
        artifacts = None
        if load_artifacts:
            artifacts = self._load_artifacts(model_name, version)
        
        return model, artifacts
    
    def _get_latest_version(self, model_name: str) -> Optional[str]:
        """Get the latest version of a model from registry or filesystem."""
        # First try registry
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            if model_name in registry and registry[model_name]:
                latest_entry = registry[model_name][-1]
                return latest_entry['version']
        
        # Fallback: scan filesystem
        model_dir = os.path.join(self.models_dir, model_name)
        if not os.path.exists(model_dir):
            return None
        
        versions = []
        for f in os.listdir(model_dir):
            if f.endswith('.pkl'):
                parts = f.replace('.pkl', '').split('_v')
                if len(parts) > 1:
                    versions.append(parts[1])
        
        if not versions:
            return None
        
        versions.sort(key=lambda v: [int(x) for x in v.split('.')])
        return versions[-1]
    
    def _load_artifacts(self, model_name: str, version: str) -> Dict[str, Any]:
        """Load artifacts associated with a model."""
        artifact_dir = os.path.join(self.artifacts_dir, f"{model_name}_v{version}")
        if not os.path.exists(artifact_dir):
            return {}
        
        artifacts = {}
        for artifact_file in os.listdir(artifact_dir):
            if artifact_file.endswith('.pkl'):
                artifact_name = artifact_file.replace('.pkl', '')
                artifact_path = os.path.join(artifact_dir, artifact_file)
                artifacts[artifact_name] = joblib.load(artifact_path)
        
        return artifacts
    
    def load_production_model(self, model_name: str) -> Tuple[Any, Optional[Dict]]:
        """
        Load the production version of a model.
        Production version is stored in a separate file or marked in registry.
        """
        prod_path = os.path.join(self.models_dir, model_name, "production.pkl")
        if os.path.exists(prod_path):
            model = joblib.load(prod_path)
            artifacts = self._load_artifacts(model_name, "production")
            return model, artifacts
        else:
            # Fallback to latest
            return self.load_model(model_name, load_artifacts=True)
    
    def list_models(self) -> List[Dict]:
        """List all models in the registry with their versions and metadata."""
        models = []
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            for model_name, versions in registry.items():
                for v in versions:
                    models.append({
                        "model_name": model_name,
                        "version": v['version'],
                        "saved_at": v['saved_at'],
                        "metrics": v.get('metrics', {})
                    })
        return models
    
    def get_model_metadata(self, model_name: str, version: Optional[str] = None) -> Dict:
        """Retrieve metadata for a model without loading the model itself."""
        if version is None:
            version = self._get_latest_version(model_name)
        
        metadata_path = os.path.join(self.metadata_dir, f"{model_name}_v{version}_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    def compare_models(self, model_name: str, metric: str = "roc_auc") -> Dict[str, float]:
        """Compare performance of different versions of a model."""
        if not os.path.exists(self.registry_path):
            return {}
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        if model_name not in registry:
            return {}
        
        comparison = {}
        for version_info in registry[model_name]:
            version = version_info['version']
            metrics = version_info.get('metrics', {})
            comparison[version] = metrics.get(metric, None)
        
        return comparison

# Convenience functions for fraud detection
_fraud_model_cache = {}

def load_fraud_model(model_name: str = "xgboost_fraud", 
                     version: Optional[str] = None,
                     use_cache: bool = True) -> Any:
    """
    Load the fraud detection model with caching.
    """
    global _fraud_model_cache
    cache_key = f"{model_name}_{version or 'latest'}"
    
    if use_cache and cache_key in _fraud_model_cache:
        return _fraud_model_cache[cache_key]
    
    loader = ModelLoader()
    model, _ = loader.load_model(model_name, version, load_artifacts=False)
    
    if use_cache:
        _fraud_model_cache[cache_key] = model
    
    return model

def load_fraud_model_with_artifacts(model_name: str = "xgboost_fraud",
                                     version: Optional[str] = None) -> Tuple[Any, Dict]:
    """
    Load fraud model along with its artifacts (scaler, encoder, feature_names).
    """
    loader = ModelLoader()
    return loader.load_model(model_name, version, load_artifacts=True)

def load_ensemble(ensemble_name: str) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Load an ensemble of models.
    
    Returns:
        Tuple of (models_dict, weights_dict)
    """
    loader = ModelLoader()
    ensemble_dir = os.path.join(loader.models_dir, f"ensemble_{ensemble_name}")
    config_path = os.path.join(ensemble_dir, "ensemble_config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Ensemble {ensemble_name} not found")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    models = {}
    for name, model_path in config['models'].items():
        models[name] = joblib.load(model_path)
    
    return models, config.get('weights', {})

if __name__ == "__main__":
    # Example
    loader = ModelLoader()
    print("Available models:", loader.list_models())
    
    # Load latest fraud model
    try:
        model, artifacts = load_fraud_model_with_artifacts()
        print(f"Loaded model: {type(model).__name__}")
        if 'scaler' in artifacts:
            print("Scaler loaded")
    except FileNotFoundError:
        print("No model found. Train a model first.")