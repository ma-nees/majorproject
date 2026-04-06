"""
Touch Screen Pattern Analyzer (Mobile/Tablet)
Analyzes touch pressure, swipe velocity, multi-touch gestures, and detects anomalies.
"""

import numpy as np
import math
from typing import List, Dict, Any, Optional

class TouchAnalyzer:
    def __init__(self):
        self.user_profiles = {}
    
    def analyze(self, touches: List[Dict], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze touch events.
        
        Args:
            touches: List of touch events with x, y, pressure, touch_radius, timestamp
            customer_id: Optional user ID for personalization
        """
        result = {
            "touch_count": len(touches),
            "avg_pressure": 0,
            "avg_touch_radius": 0,
            "swipe_velocity": 0,
            "multi_touch_count": 0,
            "anomalies": []
        }
        
        if len(touches) == 0:
            result["anomalies"].append("No touch events")
            return result
        
        # Pressure analysis
        pressures = [t.get('pressure', 0) for t in touches if 'pressure' in t]
        if pressures:
            result["avg_pressure"] = round(np.mean(pressures), 4)
            result["max_pressure"] = round(np.max(pressures), 4)
        
        # Touch radius (finger size)
        radii = [t.get('touch_radius', 0) for t in touches if 'touch_radius' in t]
        if radii:
            result["avg_touch_radius"] = round(np.mean(radii), 2)
        
        # Detect swipe gestures (consecutive touches with similar direction)
        if len(touches) >= 3:
            velocities = []
            for i in range(1, len(touches)):
                dx = touches[i]['x'] - touches[i-1]['x']
                dy = touches[i]['y'] - touches[i-1]['y']
                dt = touches[i]['timestamp'] - touches[i-1]['timestamp']
                if dt > 0:
                    vel = math.sqrt(dx*dx + dy*dy) / dt
                    velocities.append(vel)
            if velocities:
                result["avg_swipe_velocity"] = round(np.mean(velocities), 2)
                result["max_swipe_velocity"] = round(np.max(velocities), 2)
        
        # Multi-touch detection (group touches by timestamp proximity)
        # Simplified: count unique timestamps within 50ms window
        time_groups = {}
        for t in touches:
            ts = round(t['timestamp'] / 50)  # 50ms buckets
            time_groups[ts] = time_groups.get(ts, 0) + 1
        result["multi_touch_count"] = max(time_groups.values()) if time_groups else 1
        
        # Anomaly detection
        if result["avg_pressure"] > 1.2:
            result["anomalies"].append("Unusually high touch pressure (possible stylus/robot)")
        if result["avg_pressure"] < 0.1 and len(touches) > 5:
            result["anomalies"].append("Very light touch (possible automation)")
        if result.get("avg_swipe_velocity", 0) > 2000:
            result["anomalies"].append("Extremely fast swipe (script)")
        if result["multi_touch_count"] > 5:
            result["anomalies"].append("Suspicious multi-touch count")
        
        # Check for repetitive pattern (possible bot)
        if len(touches) > 20:
            # Check for identical coordinates
            coords = [(t['x'], t['y']) for t in touches]
            if len(set(coords)) < len(coords) * 0.2:
                result["anomalies"].append("Repetitive touch coordinates (automation)")
        
        # Personalization
        if customer_id and customer_id in self.user_profiles:
            profile = self.user_profiles[customer_id]
            if result["avg_pressure"] > profile.get("avg_pressure", 0.3) * 1.8:
                result["anomalies"].append("Touch pressure deviates from user baseline")
        
        result["is_anomalous"] = len(result["anomalies"]) > 0
        return result
    
    def update_user_profile(self, customer_id: str, touches: List[Dict]):
        analysis = self.analyze(touches)
        if customer_id not in self.user_profiles:
            self.user_profiles[customer_id] = {
                "avg_pressure": analysis["avg_pressure"],
                "avg_touch_radius": analysis["avg_touch_radius"],
                "samples": 1
            }
        else:
            profile = self.user_profiles[customer_id]
            alpha = 0.3
            profile["avg_pressure"] = alpha * analysis["avg_pressure"] + (1-alpha) * profile["avg_pressure"]
            profile["avg_touch_radius"] = alpha * analysis["avg_touch_radius"] + (1-alpha) * profile["avg_touch_radius"]
            profile["samples"] += 1