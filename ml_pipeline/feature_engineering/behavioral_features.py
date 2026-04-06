"""
Behavioral Features
Extracts features related to user behavior patterns: transaction history, velocity, frequency, and anomalies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

class BehavioralFeatureExtractor:
    """
    Extracts behavioral features from transaction history:
    - Velocity (transaction count in time windows)
    - Amount statistics (mean, std, ratio)
    - Spending patterns (time of day preferences, merchant diversity)
    """
    
    def __init__(self, user_history_df: Optional[pd.DataFrame] = None):
        """
        Initialize with historical transaction data for a user.
        
        Args:
            user_history_df: DataFrame with historical transactions for the user
        """
        self.history = user_history_df
        self.features = {}
    
    def set_history(self, df: pd.DataFrame):
        """Set user transaction history."""
        self.history = df.copy()
        if 'timestamp' in self.history.columns:
            self.history['timestamp'] = pd.to_datetime(self.history['timestamp'])
            self.history = self.history.sort_values('timestamp')
    
    def extract_all_features(self, current_tx: Dict, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Extract all behavioral features for a transaction.
        
        Args:
            current_tx: Current transaction dict with keys: amount, timestamp, customer_id, etc.
            lookback_days: Number of days to look back for historical data
        
        Returns:
            Dictionary of behavioral features
        """
        if self.history is None or self.history.empty:
            return self._default_features()
        
        current_time = current_tx.get('timestamp')
        if isinstance(current_time, str):
            current_time = pd.to_datetime(current_time)
        elif current_time is None:
            current_time = datetime.now()
        
        # Filter history to lookback window
        cutoff = current_time - timedelta(days=lookback_days)
        recent_history = self.history[self.history['timestamp'] >= cutoff]
        
        if recent_history.empty:
            return self._default_features()
        
        features = {}
        
        # Velocity features
        features.update(self._velocity_features(recent_history, current_time))
        
        # Amount features
        features.update(self._amount_features(recent_history, current_tx.get('amount', 0)))
        
        # Temporal features
        features.update(self._temporal_features(recent_history, current_time))
        
        # Historical fraud flags
        features.update(self._fraud_history_features(recent_history))
        
        # Behavioral consistency
        features.update(self._consistency_features(recent_history, current_tx))
        
        return features
    
    def _velocity_features(self, history: pd.DataFrame, current_time: datetime) -> Dict:
        """Transaction velocity in different time windows."""
        features = {}
        windows = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}  # hours
        
        for name, hours in windows.items():
            cutoff = current_time - timedelta(hours=hours)
            count = len(history[history['timestamp'] >= cutoff])
            features[f'velocity_{name}'] = count
        
        return features
    
    def _amount_features(self, history: pd.DataFrame, current_amount: float) -> Dict:
        """Amount-based behavioral features."""
        amounts = history['amount'].values
        
        features = {
            'avg_amount_30d': float(np.mean(amounts)),
            'std_amount_30d': float(np.std(amounts)),
            'max_amount_30d': float(np.max(amounts)),
            'min_amount_30d': float(np.min(amounts)),
            'amount_ratio_to_avg': current_amount / (np.mean(amounts) + 1e-5),
            'amount_zscore': (current_amount - np.mean(amounts)) / (np.std(amounts) + 1e-5)
        }
        return features
    
    def _temporal_features(self, history: pd.DataFrame, current_time: datetime) -> Dict:
        """Time-based behavioral patterns."""
        # Typical transaction hour for this user
        hours = history['timestamp'].dt.hour.values
        if len(hours) > 0:
            typical_hour = np.mean(hours)
            hour_deviation = abs(current_time.hour - typical_hour)
        else:
            typical_hour = 12
            hour_deviation = 0
        
        # Day of week preference
        days = history['timestamp'].dt.dayofweek.values
        if len(days) > 0:
            typical_dow = np.mean(days)
            dow_deviation = abs(current_time.weekday() - typical_dow)
        else:
            typical_dow = 2
            dow_deviation = 0
        
        # Weekend vs weekday
        is_weekend = current_time.weekday() >= 5
        weekend_ratio = (history['timestamp'].dt.dayofweek >= 5).mean() if len(history) > 0 else 0
        
        return {
            'typical_transaction_hour': float(typical_hour),
            'hour_deviation': float(hour_deviation),
            'typical_dow': float(typical_dow),
            'dow_deviation': float(dow_deviation),
            'is_weekend': int(is_weekend),
            'historical_weekend_ratio': float(weekend_ratio)
        }
    
    def _fraud_history_features(self, history: pd.DataFrame) -> Dict:
        """Features related to past fraud/chargebacks."""
        if 'is_fraud' not in history.columns:
            return {'previous_fraud_count': 0, 'fraud_rate': 0.0}
        
        fraud_count = history['is_fraud'].sum()
        fraud_rate = fraud_count / len(history) if len(history) > 0 else 0
        
        return {
            'previous_fraud_count': int(fraud_count),
            'fraud_rate': float(fraud_rate)
        }
    
    def _consistency_features(self, history: pd.DataFrame, current_tx: Dict) -> Dict:
        """Features measuring consistency with past behavior."""
        # Merchant category consistency (if available)
        current_merchant = current_tx.get('merchant_category', 'unknown')
        if 'merchant_category' in history.columns:
            unique_merchants = history['merchant_category'].nunique()
            total_tx = len(history)
            merchant_diversity = unique_merchants / total_tx if total_tx > 0 else 1
            is_common_merchant = (history['merchant_category'] == current_merchant).any()
        else:
            merchant_diversity = 1.0
            is_common_merchant = False
        
        # Device consistency
        current_device = current_tx.get('device_id', 'unknown')
        if 'device_id' in history.columns:
            devices_used = history['device_id'].nunique()
            is_known_device = (history['device_id'] == current_device).any()
            device_frequency = (history['device_id'] == current_device).mean() if len(history) > 0 else 0
        else:
            devices_used = 1
            is_known_device = False
            device_frequency = 0
        
        return {
            'merchant_diversity': float(merchant_diversity),
            'is_common_merchant': int(is_common_merchant),
            'distinct_devices_used': int(devices_used),
            'is_known_device': int(is_known_device),
            'device_frequency': float(device_frequency)
        }
    
    def _default_features(self) -> Dict:
        """Return default values when no history exists."""
        return {
            'velocity_1h': 0,
            'velocity_24h': 0,
            'velocity_7d': 0,
            'velocity_30d': 0,
            'avg_amount_30d': 0.0,
            'std_amount_30d': 0.0,
            'max_amount_30d': 0.0,
            'min_amount_30d': 0.0,
            'amount_ratio_to_avg': 1.0,
            'amount_zscore': 0.0,
            'typical_transaction_hour': 12.0,
            'hour_deviation': 0.0,
            'typical_dow': 2.0,
            'dow_deviation': 0.0,
            'is_weekend': 0,
            'historical_weekend_ratio': 0.5,
            'previous_fraud_count': 0,
            'fraud_rate': 0.0,
            'merchant_diversity': 1.0,
            'is_common_merchant': 0,
            'distinct_devices_used': 0,
            'is_known_device': 0,
            'device_frequency': 0.0
        }

# Standalone function for batch feature extraction
def extract_behavioral_features_batch(transactions_df: pd.DataFrame, 
                                       user_history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract behavioral features for multiple transactions in batch.
    
    Args:
        transactions_df: DataFrame of current transactions (one per row)
        user_history_df: Historical transactions for all users
    
    Returns:
        DataFrame with added behavioral features
    """
    features_list = []
    for idx, row in transactions_df.iterrows():
        customer_id = row.get('customer_id')
        user_history = user_history_df[user_history_df['customer_id'] == customer_id] if customer_id else None
        
        extractor = BehavioralFeatureExtractor(user_history)
        features = extractor.extract_all_features(row.to_dict())
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    return pd.concat([transactions_df.reset_index(drop=True), features_df], axis=1)

if __name__ == "__main__":
    # Example
    hist = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='D'),
        'amount': [100, 150, 200, 120, 180, 5000, 110, 130, 140, 160],
        'is_fraud': [0,0,0,0,0,1,0,0,0,0],
        'merchant_category': ['retail']*5 + ['online'] + ['retail']*4,
        'device_id': ['dev1']*10
    })
    current = {'amount': 1000, 'timestamp': datetime.now(), 'customer_id': 'user1', 'device_id': 'dev2'}
    
    extractor = BehavioralFeatureExtractor(hist)
    features = extractor.extract_all_features(current)
    print("Behavioral Features:", features)