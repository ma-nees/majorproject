"""
Advanced Model Registry with Database Backend (Optional)
For production environments with multiple models and A/B testing.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class ModelRegistryDB:
    """
    SQLite-backed model registry for tracking model versions, metrics, and deployment status.
    """
    
    def __init__(self, db_path: str = "models/registry.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    artifact_path TEXT,
                    metrics TEXT,
                    training_date TEXT,
                    is_production BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(model_name, version)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_name ON models(model_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_production ON models(is_production)
            """)
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def register_model(self, model_name: str, version: str, model_path: str,
                       artifact_path: Optional[str] = None,
                       metrics: Optional[Dict] = None,
                       set_production: bool = False):
        """Register a new model version in the database."""
        with self._get_connection() as conn:
            # Check if exists
            existing = conn.execute(
                "SELECT id FROM models WHERE model_name = ? AND version = ?",
                (model_name, version)
            ).fetchone()
            
            if existing:
                # Update
                conn.execute("""
                    UPDATE models 
                    SET model_path = ?, artifact_path = ?, metrics = ?, 
                        training_date = ?, is_production = ?
                    WHERE model_name = ? AND version = ?
                """, (model_path, artifact_path, json.dumps(metrics),
                      datetime.utcnow().isoformat(), set_production,
                      model_name, version))
            else:
                # Insert
                conn.execute("""
                    INSERT INTO models (model_name, version, model_path, artifact_path,
                                        metrics, training_date, is_production)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (model_name, version, model_path, artifact_path,
                      json.dumps(metrics), datetime.utcnow().isoformat(), set_production))
            
            # If setting as production, unset previous production for this model
            if set_production:
                conn.execute("""
                    UPDATE models SET is_production = 0 
                    WHERE model_name = ? AND version != ?
                """, (model_name, version))
    
    def get_production_model(self, model_name: str) -> Optional[Dict]:
        """Get the production model version."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM models 
                WHERE model_name = ? AND is_production = 1
            """, (model_name,)).fetchone()
            return dict(row) if row else None
    
    def get_model_version(self, model_name: str, version: str) -> Optional[Dict]:
        """Get a specific model version."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM models 
                WHERE model_name = ? AND version = ?
            """, (model_name, version)).fetchone()
            return dict(row) if row else None
    
    def list_model_versions(self, model_name: str) -> List[Dict]:
        """List all versions of a model."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT version, training_date, is_production, metrics
                FROM models 
                WHERE model_name = ?
                ORDER BY training_date DESC
            """, (model_name,)).fetchall()
            return [dict(row) for row in rows]

# Usage example
if __name__ == "__main__":
    registry = ModelRegistryDB()
    registry.register_model("xgboost_fraud", "1.0.0", "models/xgboost_v1.pkl",
                            metrics={"roc_auc": 0.95, "f1": 0.87},
                            set_production=True)
    prod = registry.get_production_model("xgboost_fraud")
    print("Production model:", prod)