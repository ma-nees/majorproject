"""
Keystroke Dynamics Analyzer
Extracts features from typing patterns and detects anomalies.
Features: hold time, flight time, digraph latencies, typing speed, rhythm consistency.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict
import math

class KeystrokeAnalyzer:
    def __init__(self):
        # Historical user profiles (in production, load from DB)
        self.user_profiles = {}  # customer_id -> profile dict
    
    def analyze(self, keystrokes: List[Dict], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze keystroke sequence and return features + anomalies.
        
        Args:
            keystrokes: List of keystroke events with keys:
                - key: character
                - press_time: timestamp (ms)
                - release_time: timestamp (ms)
                - hold_duration: ms (optional, computed if missing)
                - flight_time: ms to next key (optional)
            customer_id: Optional user ID for personalized anomaly detection
        
        Returns:
            Dictionary with extracted features and detected anomalies
        """
        if len(keystrokes) < 2:
            return {
                "avg_hold_time": 0,
                "avg_flight_time": 0,
                "typing_speed_cps": 0,
                "rhythm_variance": 0,
                "anomalies": ["Insufficient keystrokes for analysis"]
            }
        
        # Compute hold durations (time key pressed)
        hold_times = []
        for ks in keystrokes:
            if 'hold_duration' in ks:
                hold = ks['hold_duration']
            elif 'press_time' in ks and 'release_time' in ks:
                hold = ks['release_time'] - ks['press_time']
            else:
                continue
            hold_times.append(hold)
        
        # Compute flight times (time between key releases)
        flight_times = []
        for i in range(len(keystrokes) - 1):
            if 'release_time' in keystrokes[i] and 'press_time' in keystrokes[i+1]:
                flight = keystrokes[i+1]['press_time'] - keystrokes[i]['release_time']
                flight_times.append(flight)
        
        # Basic statistics
        avg_hold = np.mean(hold_times) if hold_times else 0
        avg_flight = np.mean(flight_times) if flight_times else 0
        hold_std = np.std(hold_times) if hold_times else 0
        flight_std = np.std(flight_times) if flight_times else 0
        
        # Typing speed (characters per second)
        if len(keystrokes) >= 2 and 'press_time' in keystrokes[0] and 'release_time' in keystrokes[-1]:
            total_duration = keystrokes[-1]['release_time'] - keystrokes[0]['press_time']
            if total_duration > 0:
                typing_speed = len(keystrokes) / (total_duration / 1000.0)  # chars/sec
            else:
                typing_speed = 0
        else:
            typing_speed = 0
        
        # Rhythm consistency (coefficient of variation)
        rhythm_variance = (hold_std / avg_hold) if avg_hold > 0 else 0
        
        # Detect anomalies
        anomalies = []
        # Heuristic thresholds (tune based on real data)
        if avg_hold < 30:
            anomalies.append("Abnormally fast typing (possible bot)")
        elif avg_hold > 300:
            anomalies.append("Unusually slow typing (possible hesitation)")
        
        if avg_flight < 10:
            anomalies.append("Virtually no flight time (macro/script)")
        elif avg_flight > 500:
            anomalies.append("Long pauses between keys")
        
        if typing_speed > 15:
            anomalies.append("Extremely high typing speed (>15 cps)")
        
        if rhythm_variance > 1.5:
            anomalies.append("Highly inconsistent rhythm")
        
        # Personalized anomaly detection if user profile exists
        if customer_id and customer_id in self.user_profiles:
            profile = self.user_profiles[customer_id]
            if avg_hold > profile.get('avg_hold', 150) * 1.5:
                anomalies.append("Hold time significantly deviates from user baseline")
            if typing_speed < profile.get('typing_speed', 5) * 0.5:
                anomalies.append("Typing speed much slower than usual")
        
        return {
            "avg_hold_time": round(avg_hold, 2),
            "avg_flight_time": round(avg_flight, 2),
            "hold_time_std": round(hold_std, 2),
            "flight_time_std": round(flight_std, 2),
            "typing_speed_cps": round(typing_speed, 2),
            "rhythm_variance": round(rhythm_variance, 4),
            "keystroke_count": len(keystrokes),
            "anomalies": anomalies,
            "is_anomalous": len(anomalies) > 0
        }
    
    def update_user_profile(self, customer_id: str, keystrokes: List[Dict]):
        """Update the user's baseline profile with new keystroke data."""
        analysis = self.analyze(keystrokes)
        if customer_id not in self.user_profiles:
            self.user_profiles[customer_id] = {
                "avg_hold": analysis["avg_hold_time"],
                "typing_speed": analysis["typing_speed_cps"],
                "samples": 1
            }
        else:
            profile = self.user_profiles[customer_id]
            # Exponential moving average
            alpha = 0.3
            profile["avg_hold"] = alpha * analysis["avg_hold_time"] + (1-alpha) * profile["avg_hold"]
            profile["typing_speed"] = alpha * analysis["typing_speed_cps"] + (1-alpha) * profile["typing_speed"]
            profile["samples"] += 1