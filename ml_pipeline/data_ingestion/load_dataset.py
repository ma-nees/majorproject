"""
Dataset Loader Module
Handles loading raw transaction data from various sources (CSV, Parquet, JSON, Database).
Performs initial validation and basic cleaning.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    Unified data loader for transaction datasets.
    Supports CSV, Parquet, JSON, and database connections.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the DataLoader.
        
        Args:
            data_path: Path to data file or directory (can be set later)
        """
        self.data_path = data_path
        self.raw_data = None
        self.metadata = {}
    
    def load_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv arguments
        
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading CSV from {file_path}")
        default_kwargs = {
            'encoding': 'utf-8',
            'low_memory': False
        }
        default_kwargs.update(kwargs)
        df = pd.read_csv(file_path, **default_kwargs)
        self.raw_data = df
        self.metadata['source'] = file_path
        self.metadata['rows'] = len(df)
        self.metadata['columns'] = list(df.columns)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_parquet(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load data from Parquet file."""
        logger.info(f"Loading Parquet from {file_path}")
        df = pd.read_parquet(file_path, **kwargs)
        self.raw_data = df
        self.metadata['source'] = file_path
        self.metadata['rows'] = len(df)
        self.metadata['columns'] = list(df.columns)
        return df
    
    def load_json(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load data from JSON file (line-delimited or array)."""
        logger.info(f"Loading JSON from {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            # Try line-delimited JSON
            f.seek(0)
            lines = [json.loads(line) for line in f if line.strip()]
            df = pd.DataFrame(lines)
        
        self.raw_data = df
        self.metadata['source'] = file_path
        self.metadata['rows'] = len(df)
        return df
    
    def load_from_directory(self, directory_path: str, file_pattern: str = "*.csv") -> pd.DataFrame:
        """
        Load and concatenate multiple files from a directory.
        
        Args:
            directory_path: Path to directory containing data files
            file_pattern: Glob pattern (e.g., "*.csv", "*.parquet", "transaction_*.json")
        """
        from glob import glob
        path = Path(directory_path)
        files = list(path.glob(file_pattern))
        
        if not files:
            raise FileNotFoundError(f"No files matching {file_pattern} in {directory_path}")
        
        logger.info(f"Loading {len(files)} files from {directory_path}")
        dfs = []
        for file in files:
            if file.suffix == '.csv':
                df = pd.read_csv(file)
            elif file.suffix == '.parquet':
                df = pd.read_parquet(file)
            elif file.suffix == '.json':
                df = self.load_json(str(file))
            else:
                logger.warning(f"Skipping unsupported file type: {file}")
                continue
            dfs.append(df)
        
        combined_df = pd.concat(dfs, ignore_index=True)
        self.raw_data = combined_df
        self.metadata['source'] = directory_path
        self.metadata['files_loaded'] = len(files)
        self.metadata['rows'] = len(combined_df)
        return combined_df
    
    def load_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """
        Load data from a SQL database.
        
        Args:
            connection_string: SQLAlchemy connection string
            query: SQL query to execute
        """
        try:
            from sqlalchemy import create_engine
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine)
            engine.dispose()
            self.raw_data = df
            self.metadata['source'] = 'database'
            self.metadata['rows'] = len(df)
            return df
        except ImportError:
            raise ImportError("SQLAlchemy not installed. Run: pip install sqlalchemy")
    
    def validate_schema(self, expected_columns: List[str], strict: bool = False) -> Dict[str, Any]:
        """
        Validate that the loaded data has the expected schema.
        
        Args:
            expected_columns: List of required column names
            strict: If True, raise error on missing columns; else warn
        
        Returns:
            Dictionary with validation results
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_* method first.")
        
        actual_columns = set(self.raw_data.columns)
        expected_set = set(expected_columns)
        missing = expected_set - actual_columns
        extra = actual_columns - expected_set
        
        result = {
            "valid": len(missing) == 0,
            "missing_columns": list(missing),
            "extra_columns": list(extra),
            "total_expected": len(expected_columns),
            "total_actual": len(actual_columns)
        }
        
        if missing:
            msg = f"Missing expected columns: {missing}"
            if strict:
                raise ValueError(msg)
            else:
                logger.warning(msg)
        
        return result
    
    def get_preview(self, n_rows: int = 5) -> pd.DataFrame:
        """Return a preview of the loaded data."""
        if self.raw_data is None:
            return pd.DataFrame()
        return self.raw_data.head(n_rows)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Generate basic statistics about the loaded dataset."""
        if self.raw_data is None:
            return {}
        
        return {
            "shape": self.raw_data.shape,
            "memory_usage_mb": self.raw_data.memory_usage(deep=True).sum() / (1024 * 1024),
            "null_counts": self.raw_data.isnull().sum().to_dict(),
            "data_types": self.raw_data.dtypes.astype(str).to_dict(),
            "metadata": self.metadata
        }

# Convenience function for quick loading
def load_transaction_data(source_path: str, file_type: str = "auto") -> pd.DataFrame:
    """
    Quick helper to load transaction data.
    
    Args:
        source_path: Path to file or directory
        file_type: 'csv', 'parquet', 'json', 'auto', or 'directory'
    """
    loader = DataLoader()
    
    if file_type == "directory":
        return loader.load_from_directory(source_path)
    
    if file_type == "auto":
        ext = Path(source_path).suffix.lower()
        if ext == '.csv':
            return loader.load_csv(source_path)
        elif ext == '.parquet':
            return loader.load_parquet(source_path)
        elif ext == '.json':
            return loader.load_json(source_path)
        else:
            raise ValueError(f"Unknown file extension: {ext}")
    elif file_type == 'csv':
        return loader.load_csv(source_path)
    elif file_type == 'parquet':
        return loader.load_parquet(source_path)
    elif file_type == 'json':
        return loader.load_json(source_path)
    else:
        raise ValueError(f"Unsupported file_type: {file_type}")

# Example usage
if __name__ == "__main__":
    # Load sample data
    loader = DataLoader()
    df = loader.load_csv("data/raw/transaction_data.csv")
    print(loader.get_preview())
    print(loader.get_statistics())