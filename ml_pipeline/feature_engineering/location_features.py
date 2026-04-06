"""
Location Features
Extracts features from transaction geolocation, IP address, and distance metrics.
"""

import math
import re
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import numpy as np

class LocationFeatureExtractor:
    """
    Extracts location-based features:
    - Distance from typical user location
    - IP risk indicators (proxy, VPN, TOR)
    - Country risk scoring
    - Distance between consecutive transactions
    """
    
    def __init__(self, user_typical_locations: Optional[pd.DataFrame] = None,
                 ip_risk_db: Optional[Dict] = None):
        """
        Args:
            user_typical_locations: DataFrame with user_id, typical_lat, typical_lon
            ip_risk_db: Dict mapping IP ranges to risk scores
        """
        self.user_locations = user_typical_locations if user_typical_locations is not None else pd.DataFrame()
        self.ip_risk_db = ip_risk_db or {}
        
        # Country risk scores (0=low risk, 1=high risk)
        self.country_risk = {
            'US': 0.2, 'CA': 0.2, 'UK': 0.2, 'DE': 0.2, 'FR': 0.2, 'AU': 0.2,
            'RU': 0.7, 'CN': 0.6, 'NG': 0.8, 'UA': 0.6, 'BR': 0.5, 'IN': 0.4,
            'ID': 0.5, 'VN': 0.6, 'PH': 0.5, 'PK': 0.7, 'BD': 0.6
        }
    
    def extract_features(self, transaction: Dict[str, Any], user_id: Optional[str] = None,
                         prev_transaction: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract location-based features for a transaction.
        
        Args:
            transaction: Dict with lat, lon, ip_address, country_code, city
            user_id: User identifier for typical location lookup
            prev_transaction: Previous transaction (for distance traveled)
        
        Returns:
            Dictionary of location features
        """
        features = {}
        
        # Current location
        lat = transaction.get('lat')
        lon = transaction.get('lon')
        features['has_coordinates'] = int(lat is not None and lon is not None)
        
        if lat and lon:
            features['latitude'] = float(lat)
            features['longitude'] = float(lon)
        
        # IP address features
        ip = transaction.get('ip_address', '')
        ip_features = self._extract_ip_features(ip)
        features.update(ip_features)
        
        # Country features
        country = transaction.get('country_code', '')
        features['country_code'] = country
        features['country_risk_score'] = self.country_risk.get(country, 0.3)
        features['is_high_risk_country'] = int(features['country_risk_score'] >= 0.6)
        
        # Distance from typical user location
        if user_id and not self.user_locations.empty:
            user_loc = self.user_locations[self.user_locations['user_id'] == user_id]
            if not user_loc.empty and lat and lon:
                typical_lat = user_loc.iloc[0]['typical_lat']
                typical_lon = user_loc.iloc[0]['typical_lon']
                distance = self._haversine_distance(lat, lon, typical_lat, typical_lon)
                features['distance_from_typical_km'] = round(distance, 2)
                features['is_unusual_location'] = int(distance > 100)  # >100km
            else:
                features['distance_from_typical_km'] = -1
                features['is_unusual_location'] = 0
        else:
            features['distance_from_typical_km'] = -1
            features['is_unusual_location'] = 0
        
        # Distance from previous transaction
        if prev_transaction:
            prev_lat = prev_transaction.get('lat')
            prev_lon = prev_transaction.get('lon')
            prev_time = prev_transaction.get('timestamp')
            current_time = transaction.get('timestamp')
            
            if prev_lat and prev_lon and lat and lon and prev_time and current_time:
                distance = self._haversine_distance(lat, lon, prev_lat, prev_lon)
                time_diff = (current_time - prev_time).total_seconds() / 3600  # hours
                features['distance_from_prev_km'] = round(distance, 2)
                features['time_since_prev_hours'] = round(time_diff, 2)
                if time_diff > 0:
                    speed = distance / time_diff  # km/h
                    features['travel_speed_kmh'] = round(speed, 2)
                    features['impossible_travel'] = int(speed > 800)  # >800 km/h impossible
                else:
                    features['travel_speed_kmh'] = 0
                    features['impossible_travel'] = 0
            else:
                features['distance_from_prev_km'] = -1
                features['time_since_prev_hours'] = -1
                features['travel_speed_kmh'] = 0
                features['impossible_travel'] = 0
        else:
            features['distance_from_prev_km'] = -1
            features['time_since_prev_hours'] = -1
            features['travel_speed_kmh'] = 0
            features['impossible_travel'] = 0
        
        # City/region mismatch
        city = transaction.get('city', '')
        if city and country:
            features['has_city_info'] = 1
        else:
            features['has_city_info'] = 0
        
        return features
    
    def _extract_ip_features(self, ip: str) -> Dict[str, Any]:
        """Extract risk features from IP address."""
        features = {
            'is_proxy': 0,
            'is_vpn': 0,
            'is_tor': 0,
            'is_datacenter': 0,
            'ip_reputation_score': 0.5
        }
        
        if not ip or ip == '0.0.0.0':
            features['ip_reputation_score'] = 0.8  # missing IP is suspicious
            return features
        
        # Private IP ranges
        private_patterns = [
            r'^10\.', r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', r'^192\.168\.', r'^127\.', r'^0\.'
        ]
        is_private = any(re.match(p, ip) for p in private_patterns)
        features['is_private_ip'] = int(is_private)
        
        # Simple reputation heuristics (in production, use IP intelligence API)
        # Check for common proxy/VPN indicators in IP (simplified)
        first_octet = int(ip.split('.')[0]) if '.' in ip else 0
        if first_octet in [45, 46, 47, 80, 81, 82]:  # common datacenter ranges
            features['is_datacenter'] = 1
            features['ip_reputation_score'] = 0.6
        
        # TOR exit nodes (would need external list)
        # For now, just placeholder
        features['is_tor'] = 0
        
        return features
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in km."""
        R = 6371  # Earth's radius in km
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def update_user_location(self, user_id: str, lat: float, lon: float):
        """Update typical user location (e.g., after transaction)."""
        # In production, maintain a moving average or use clustering
        if self.user_locations.empty:
            new_df = pd.DataFrame([{'user_id': user_id, 'typical_lat': lat, 'typical_lon': lon}])
            self.user_locations = new_df
        else:
            mask = self.user_locations['user_id'] == user_id
            if mask.any():
                idx = self.user_locations[mask].index[0]
                # Exponential moving average
                alpha = 0.3
                self.user_locations.loc[idx, 'typical_lat'] = (alpha * lat + 
                    (1-alpha) * self.user_locations.loc[idx, 'typical_lat'])
                self.user_locations.loc[idx, 'typical_lon'] = (alpha * lon + 
                    (1-alpha) * self.user_locations.loc[idx, 'typical_lon'])
            else:
                self.user_locations = pd.concat([self.user_locations, 
                    pd.DataFrame([{'user_id': user_id, 'typical_lat': lat, 'typical_lon': lon}])],
                    ignore_index=True)

# Batch location feature extraction
def extract_location_features_batch(transactions_df: pd.DataFrame,
                                     user_locations_df: Optional[pd.DataFrame] = None,
                                     sort_by_user_and_time: bool = True) -> pd.DataFrame:
    """
    Extract location features for a batch of transactions.
    If sort_by_user_and_time, will compute distances to previous transaction per user.
    """
    extractor = LocationFeatureExtractor(user_locations_df)
    
    if sort_by_user_and_time and 'customer_id' in transactions_df.columns and 'timestamp' in transactions_df.columns:
        transactions_df = transactions_df.sort_values(['customer_id', 'timestamp'])
    
    features_list = []
    prev_tx_by_user = {}
    
    for _, row in transactions_df.iterrows():
        user_id = row.get('customer_id')
        prev_tx = prev_tx_by_user.get(user_id) if user_id else None
        
        features = extractor.extract_features(row.to_dict(), user_id, prev_tx)
        features_list.append(features)
        
        # Update previous transaction for this user
        if user_id:
            prev_tx_by_user[user_id] = row.to_dict()
    
    features_df = pd.DataFrame(features_list)
    return pd.concat([transactions_df.reset_index(drop=True), features_df], axis=1)

if __name__ == "__main__":
    sample_tx = {
        'lat': 40.7128,
        'lon': -74.0060,
        'ip_address': '192.168.1.1',
        'country_code': 'US',
        'city': 'New York',
        'timestamp': pd.Timestamp.now()
    }
    prev_tx = {
        'lat': 34.0522,
        'lon': -118.2437,
        'timestamp': pd.Timestamp.now() - pd.Timedelta(hours=5)
    }
    extractor = LocationFeatureExtractor()
    features = extractor.extract_features(sample_tx, user_id='user1', prev_transaction=prev_tx)
    print("Location Features:", features)