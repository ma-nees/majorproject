# anomaly_detection/behavior_monitor.py
import pandas as pd
import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class BehaviorMonitor:
    """
    Tracks per-user behavioral statistics over sliding windows.
    Detects deviations from historical patterns.
    """
    
    def __init__(self, window_minutes: int = 60, max_history: int = 100):
        """
        Args:
            window_minutes: Time window for velocity checks (e.g., transactions in last hour)
            max_history: Maximum number of past transactions to keep per user
        """
        self.window_minutes = window_minutes
        self.max_history = max_history
        # user_id -> deque of (timestamp, amount, location, device_id)
        self.user_history = defaultdict(lambda: deque(maxlen=max_history))
    
    def add_transaction(self, user_id: str, timestamp: datetime,
                        amount: float, location: str = None, device_id: str = None):
        """Record a transaction for a user."""
        self.user_history[user_id].append({
            'timestamp': timestamp,
            'amount': amount,
            'location': location,
            'device_id': device_id
        })
    
    def get_velocity(self, user_id: str, current_time: datetime) -> int:
        """
        Number of transactions in the last `window_minutes` minutes.
        """
        cutoff = current_time - timedelta(minutes=self.window_minutes)
        history = self.user_history.get(user_id, [])
        count = sum(1 for txn in history if txn['timestamp'] >= cutoff)
        return count
    
    def get_avg_amount(self, user_id: str, lookback_minutes: int = None) -> float:
        """
        Average transaction amount for the user (over recent history or all).
        """
        history = self.user_history.get(user_id, [])
        if not history:
            return 0.0
        if lookback_minutes:
            cutoff = datetime.now() - timedelta(minutes=lookback_minutes)
            amounts = [txn['amount'] for txn in history if txn['timestamp'] >= cutoff]
        else:
            amounts = [txn['amount'] for txn in history]
        return np.mean(amounts) if amounts else 0.0
    
    def amount_deviation_score(self, user_id: str, current_amount: float,
                               lookback_minutes: int = None) -> float:
        """
        Returns a score (0-1) indicating how unusual the amount is.
        Uses z-score relative to user's historical amounts.
        """
        history = self.user_history.get(user_id, [])
        if not history:
            return 0.0  # no history, not unusual
        if lookback_minutes:
            cutoff = datetime.now() - timedelta(minutes=lookback_minutes)
            amounts = [txn['amount'] for txn in history if txn['timestamp'] >= cutoff]
        else:
            amounts = [txn['amount'] for txn in history]
        if len(amounts) < 2:
            return 0.0
        mean = np.mean(amounts)
        std = np.std(amounts)
        if std == 0:
            return 0.0
        z = abs(current_amount - mean) / std
        # Convert z to score: z=2 -> 0.5, z=4 -> 0.84 (sigmoid-like)
        score = 1 - 2 / (1 + np.exp(z / 2))  # range [0,1)
        return min(score, 0.99)
    
    def location_change_risk(self, user_id: str, current_location: str) -> float:
        """
        Returns risk score (0-1) if the current location is new or different from typical.
        """
        history = self.user_history.get(user_id, [])
        if not history or current_location is None:
            return 0.0
        past_locations = [txn['location'] for txn in history if txn['location']]
        if not past_locations:
            return 0.0
        # If current location never seen before -> high risk
        if current_location not in past_locations:
            return 0.8
        # If location is frequent but recent changes? can be more sophisticated
        return 0.0
    
    def device_change_risk(self, user_id: str, current_device: str) -> float:
        """Similar to location, returns risk for new device."""
        history = self.user_history.get(user_id, [])
        if not history or current_device is None:
            return 0.0
        past_devices = [txn['device_id'] for txn in history if txn['device_id']]
        if not past_devices:
            return 0.0
        if current_device not in past_devices:
            return 0.7
        return 0.0
    
    def get_behavioral_risk_score(self, user_id: str, timestamp: datetime,
                                   amount: float, location: str = None,
                                   device_id: str = None) -> Dict[str, float]:
        """
        Computes a combined behavioral risk score and individual components.
        """
        velocity = self.get_velocity(user_id, timestamp)
        # Velocity risk: more than 5 txns in window -> high risk
        velocity_risk = min(velocity / 10.0, 1.0)
        
        amount_risk = self.amount_deviation_score(user_id, amount)
        location_risk = self.location_change_risk(user_id, location)
        device_risk = self.device_change_risk(user_id, device_id)
        
        # Weighted combination (adjust weights as needed)
        total_risk = (0.3 * velocity_risk +
                      0.3 * amount_risk +
                      0.2 * location_risk +
                      0.2 * device_risk)
        
        return {
            'velocity_risk': velocity_risk,
            'amount_risk': amount_risk,
            'location_risk': location_risk,
            'device_risk': device_risk,
            'behavioral_risk_score': total_risk
        }
    
    def update_and_score(self, user_id: str, timestamp: datetime,
                         amount: float, location: str = None,
                         device_id: str = None) -> float:
        """
        Add the transaction and return the behavioral risk score.
        """
        risk_info = self.get_behavioral_risk_score(user_id, timestamp, amount, location, device_id)
        # Add after scoring (so current transaction not used in its own history)
        self.add_transaction(user_id, timestamp, amount, location, device_id)
        return risk_info['behavioral_risk_score']


# Example usage for real-time monitoring
class GlobalBehaviorMonitor:
    """Singleton-style monitor that can be imported across modules."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.monitor = BehaviorMonitor(window_minutes=60)
        return cls._instance
    
    def get_monitor(self) -> BehaviorMonitor:
        return self.monitor