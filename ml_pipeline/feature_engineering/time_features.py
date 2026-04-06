"""
Time Features
Extracts temporal features from transaction timestamps: hour, day, week, season, time since last activity, etc.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class TimeFeatureExtractor:
    """
    Extracts time-based features from transaction timestamp.
    Includes cyclical encoding, time since last event, and behavioral time patterns.
    """
    
    def __init__(self):
        pass
    
    def extract_features(self, timestamp: Any, last_activity_time: Optional[datetime] = None,
                         timezone_offset: int = 0) -> Dict[str, Any]:
        """
        Extract time features from a timestamp.
        
        Args:
            timestamp: Timestamp of the transaction (datetime or string)
            last_activity_time: Previous transaction timestamp for this user
            timezone_offset: Offset in hours from UTC (e.g., -5 for EST)
        
        Returns:
            Dictionary of time features
        """
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        # Adjust for timezone if needed (simple offset)
        local_time = timestamp + timedelta(hours=timezone_offset)
        
        features = {}
        
        # Basic temporal features
        features['year'] = local_time.year
        features['month'] = local_time.month
        features['day'] = local_time.day
        features['hour'] = local_time.hour
        features['minute'] = local_time.minute
        features['day_of_week'] = local_time.weekday()  # 0=Monday
        features['quarter'] = (local_time.month - 1) // 3 + 1
        
        # Cyclical encoding (preserves circular nature of time)
        features['hour_sin'] = np.sin(2 * np.pi * local_time.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * local_time.hour / 24)
        features['day_sin'] = np.sin(2 * np.pi * local_time.weekday() / 7)
        features['day_cos'] = np.cos(2 * np.pi * local_time.weekday() / 7)
        features['month_sin'] = np.sin(2 * np.pi * local_time.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * local_time.month / 12)
        
        # Boolean flags
        features['is_weekend'] = int(local_time.weekday() >= 5)
        features['is_business_hours'] = int(9 <= local_time.hour < 17)
        features['is_night'] = int(22 <= local_time.hour or local_time.hour < 5)
        features['is_lunch_hour'] = int(12 <= local_time.hour < 14)
        features['is_early_morning'] = int(5 <= local_time.hour < 8)
        features['is_evening'] = int(17 <= local_time.hour < 22)
        
        # Day of week name (categorical, could be one-hot encoded later)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        features['day_name'] = day_names[local_time.weekday()]
        
        # Week of year
        features['week_of_year'] = local_time.isocalendar()[1]
        features['is_weekend'] = int(local_time.weekday() >= 5)
        
        # Season
        month = local_time.month
        if month in [12, 1, 2]:
            features['season'] = 'winter'
        elif month in [3, 4, 5]:
            features['season'] = 'spring'
        elif month in [6, 7, 8]:
            features['season'] = 'summer'
        else:
            features['season'] = 'fall'
        
        # Holiday proximity (simplified - could use holiday calendar)
        features['days_to_christmas'] = self._days_until(local_time, 12, 25)
        features['days_to_new_year'] = self._days_until(local_time, 1, 1)
        features['is_black_friday_week'] = int(local_time.month == 11 and 22 <= local_time.day <= 28)
        
        # Time since last activity (if provided)
        if last_activity_time:
            if isinstance(last_activity_time, str):
                last_activity_time = pd.to_datetime(last_activity_time)
            time_diff = timestamp - last_activity_time
            features['hours_since_last_tx'] = round(time_diff.total_seconds() / 3600, 2)
            features['days_since_last_tx'] = round(time_diff.total_seconds() / 86400, 2)
            features['minutes_since_last_tx'] = round(time_diff.total_seconds() / 60, 2)
            features['is_first_tx_of_day'] = int(features['hours_since_last_tx'] > 24)
        else:
            features['hours_since_last_tx'] = -1
            features['days_since_last_tx'] = -1
            features['minutes_since_last_tx'] = -1
            features['is_first_tx_of_day'] = 1
        
        # Frequency encoding (for later aggregation)
        features['time_bucket'] = self._get_time_bucket(local_time)
        
        return features
    
    def _days_until(self, current_date: datetime, target_month: int, target_day: int) -> int:
        """Calculate days until next occurrence of a date."""
        target = datetime(current_date.year, target_month, target_day)
        if target < current_date:
            target = datetime(current_date.year + 1, target_month, target_day)
        return (target - current_date).days
    
    def _get_time_bucket(self, dt: datetime) -> str:
        """Categorize time into buckets for aggregation."""
        hour = dt.hour
        if hour < 6:
            return 'late_night'
        elif hour < 12:
            return 'morning'
        elif hour < 17:
            return 'afternoon'
        elif hour < 22:
            return 'evening'
        else:
            return 'late_evening'
    
    def extract_batch(self, timestamps: List[Any], last_activity_times: Optional[List[datetime]] = None) -> pd.DataFrame:
        """
        Extract time features for a batch of timestamps.
        
        Args:
            timestamps: List of timestamps
            last_activity_times: List of previous activity times (same length)
        
        Returns:
            DataFrame with time features
        """
        if last_activity_times is None:
            last_activity_times = [None] * len(timestamps)
        
        features_list = []
        for ts, last_ts in zip(timestamps, last_activity_times):
            features = self.extract_features(ts, last_ts)
            features_list.append(features)
        
        return pd.DataFrame(features_list)

# Batch feature extraction for transactions DataFrame
def extract_time_features_batch(transactions_df: pd.DataFrame, 
                                timezone_offset: int = 0,
                                user_last_tx_map: Optional[Dict[str, datetime]] = None) -> pd.DataFrame:
    """
    Extract time features for all transactions in a DataFrame.
    
    Args:
        transactions_df: DataFrame with 'timestamp' column (and optional 'customer_id')
        timezone_offset: Timezone offset in hours
        user_last_tx_map: Optional dict mapping user_id to last transaction time
    
    Returns:
        DataFrame with added time features
    """
    extractor = TimeFeatureExtractor()
    
    # If user_last_tx_map not provided, compute on the fly
    if user_last_tx_map is None and 'customer_id' in transactions_df.columns:
        # Sort by user and time
        df_sorted = transactions_df.sort_values(['customer_id', 'timestamp'])
        user_last_tx = {}
        last_times = []
        for _, row in df_sorted.iterrows():
            user_id = row.get('customer_id')
            ts = row['timestamp']
            last_ts = user_last_tx.get(user_id)
            last_times.append(last_ts)
            user_last_tx[user_id] = ts
        # Reorder back to original order
        df_sorted['_last_tx'] = last_times
        df_sorted = df_sorted.sort_index()
        last_activity_times = df_sorted['_last_tx'].tolist()
    else:
        last_activity_times = [user_last_tx_map.get(row.get('customer_id')) if user_last_tx_map else None 
                               for _, row in transactions_df.iterrows()]
    
    timestamps = transactions_df['timestamp'].tolist()
    features_df = extractor.extract_batch(timestamps, last_activity_times)
    
    # Adjust timezone offset if needed
    if timezone_offset != 0:
        # This would require adjusting hour and cyclical features
        # For simplicity, we assume timestamps are already in local time or UTC
        pass
    
    return pd.concat([transactions_df.reset_index(drop=True), features_df], axis=1)

# Additional time-based risk features
def add_time_risk_features(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived risk features based on time patterns.
    """
    # High-risk time periods
    features_df['is_high_risk_hour'] = ((features_df['hour'] >= 1) & (features_df['hour'] <= 4)).astype(int)
    features_df['is_high_risk_day'] = ((features_df['day_of_week'] == 6) | (features_df['day_of_week'] == 0)).astype(int)
    
    # Unusual time score (if user has typical pattern, otherwise 0)
    if 'hour_sin' in features_df.columns and 'hour_cos' in features_df.columns:
        # Placeholder: actual deviation would require user profile
        features_df['hour_deviation_score'] = 0.0
    
    return features_df

if __name__ == "__main__":
    # Example
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    extractor = TimeFeatureExtractor()
    features = extractor.extract_features(now, last_activity_time=yesterday)
    print("Time Features:", features)
    
    # Batch example
    df = pd.DataFrame({
        'timestamp': [now, yesterday, now - timedelta(hours=3)],
        'customer_id': ['user1', 'user1', 'user2']
    })
    result_df = extract_time_features_batch(df)
    print("\nBatch result:\n", result_df[['timestamp', 'hour', 'day_of_week', 'hours_since_last_tx']])