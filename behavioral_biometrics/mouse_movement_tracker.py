"""
Mouse Movement & Click Analyzer
Tracks mouse trajectory, velocity, acceleration, click patterns, and detects robotic/macro behavior.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque

class MouseAnalyzer:
    def __init__(self):
        self.user_profiles = {}
    
    def analyze(self, movements: List[Dict], clicks: List[Dict], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze mouse movements and clicks.
        
        Args:
            movements: List of movement samples with x, y, timestamp, velocity, acceleration
            clicks: List of click events with x, y, button, timestamp, click_duration
            customer_id: Optional user ID for personalization
        """
        result = {
            "total_movements": len(movements),
            "total_clicks": len(clicks),
            "avg_velocity": 0,
            "avg_acceleration": 0,
            "jerkiness": 0,
            "click_frequency": 0,
            "anomalies": []
        }
        
        if len(movements) == 0:
            result["anomalies"].append("No mouse movement detected")
            return result
        
        # Compute velocities and accelerations if not provided
        velocities = []
        accelerations = []
        for i, m in enumerate(movements):
            if 'velocity' in m:
                velocities.append(m['velocity'])
            else:
                # Compute from consecutive points
                if i > 0:
                    dx = m['x'] - movements[i-1]['x']
                    dy = m['y'] - movements[i-1]['y']
                    dt = m['timestamp'] - movements[i-1]['timestamp']
                    if dt > 0:
                        vel = math.sqrt(dx*dx + dy*dy) / dt
                        velocities.append(vel)
                        if i > 1 and len(velocities) >= 2:
                            acc = (velocities[-1] - velocities[-2]) / dt
                            accelerations.append(acc)
        
        result["avg_velocity"] = round(np.mean(velocities), 2) if velocities else 0
        result["avg_acceleration"] = round(np.mean(accelerations), 2) if accelerations else 0
        
        # Jerkiness: variation in acceleration (higher = more erratic)
        if len(accelerations) > 1:
            result["jerkiness"] = round(np.std(accelerations), 2)
        
        # Click analysis
        if clicks:
            click_times = [c['timestamp'] for c in clicks]
            if len(click_times) > 1:
                intervals = np.diff(click_times)
                avg_click_interval = np.mean(intervals)
                result["avg_click_interval_ms"] = round(avg_click_interval, 2)
                result["click_frequency"] = round(1000 / avg_click_interval if avg_click_interval > 0 else 0, 2)
            else:
                result["avg_click_interval_ms"] = 0
                result["click_frequency"] = 0
        else:
            result["avg_click_interval_ms"] = 0
            result["click_frequency"] = 0
        
        # Anomaly detection
        if result["avg_velocity"] > 3000:
            result["anomalies"].append("Extremely fast mouse movement (possible script)")
        if result["avg_acceleration"] > 5000:
            result["anomalies"].append("Impossibly high acceleration (automation)")
        if result["jerkiness"] > 200:
            result["anomalies"].append("Erratic mouse trajectory")
        if result["click_frequency"] > 15:
            result["anomalies"].append("Rapid clicking pattern (macro)")
        
        # Detect straight lines (typical of bots)
        if len(movements) > 10:
            # Simple straightness measure: standard deviation of angle changes
            angles = []
            for i in range(2, len(movements)):
                dx1 = movements[i-1]['x'] - movements[i-2]['x']
                dy1 = movements[i-1]['y'] - movements[i-2]['y']
                dx2 = movements[i]['x'] - movements[i-1]['x']
                dy2 = movements[i]['y'] - movements[i-1]['y']
                if dx1 != 0 or dy1 != 0:
                    angle1 = math.atan2(dy1, dx1)
                    angle2 = math.atan2(dy2, dx2)
                    angle_change = abs(angle2 - angle1)
                    angles.append(angle_change)
            if angles and np.std(angles) < 0.1:
                result["anomalies"].append("Perfectly straight mouse path (automation)")
        
        # Personalization
        if customer_id and customer_id in self.user_profiles:
            profile = self.user_profiles[customer_id]
            if result["avg_velocity"] > profile.get("avg_velocity", 500) * 2:
                result["anomalies"].append("Mouse speed far above user baseline")
        
        result["is_anomalous"] = len(result["anomalies"]) > 0
        return result
    
    def update_user_profile(self, customer_id: str, movements: List[Dict], clicks: List[Dict]):
        analysis = self.analyze(movements, clicks)
        if customer_id not in self.user_profiles:
            self.user_profiles[customer_id] = {
                "avg_velocity": analysis["avg_velocity"],
                "avg_acceleration": analysis["avg_acceleration"],
                "samples": 1
            }
        else:
            profile = self.user_profiles[customer_id]
            alpha = 0.3
            profile["avg_velocity"] = alpha * analysis["avg_velocity"] + (1-alpha) * profile["avg_velocity"]
            profile["avg_acceleration"] = alpha * analysis["avg_acceleration"] + (1-alpha) * profile["avg_acceleration"]
            profile["samples"] += 1