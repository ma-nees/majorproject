"""
Session Behavior Model
Builds user behavioral profiles across sessions and detects anomalies using statistical models.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

class SessionBehaviorModel:
    def __init__(self):
        # Store historical session data per user
        self.user_history = defaultdict(list)
    
    def build_profile(self, sessions: List[Dict]) -> Dict[str, Any]:
        """
        Build a behavioral profile from past sessions.
        
        Args:
            sessions: List of session dicts with fields like:
                - keystroke_pattern (dict from keystroke analysis)
                - mouse_movements (dict from mouse analysis)
                - touch_pattern (dict from touch analysis)
                - behavioral_risk_score
                - created_at
        """
        if not sessions:
            return {
                "avg_keystroke_speed": None,
                "avg_mouse_speed": None,
                "rhythm_pattern": None,
                "session_count": 0
            }
        
        keystroke_speeds = []
        mouse_speeds = []
        hold_times = []
        flight_times = []
        
        for sess in sessions:
            # Extract keystroke features
            ks = sess.get('keystroke_pattern', {})
            if ks and 'last_analysis' in ks:
                ana = ks['last_analysis']
                if ana.get('typing_speed_cps'):
                    keystroke_speeds.append(ana['typing_speed_cps'])
                if ana.get('avg_hold_time'):
                    hold_times.append(ana['avg_hold_time'])
                if ana.get('avg_flight_time'):
                    flight_times.append(ana['avg_flight_time'])
            
            # Extract mouse features
            ms = sess.get('mouse_movements', {})
            if ms and 'last_analysis' in ms:
                mouse_speeds.append(ms['last_analysis'].get('avg_velocity', 0))
        
        profile = {
            "avg_keystroke_speed": round(np.mean(keystroke_speeds), 2) if keystroke_speeds else None,
            "std_keystroke_speed": round(np.std(keystroke_speeds), 2) if keystroke_speeds else None,
            "avg_mouse_speed": round(np.mean(mouse_speeds), 2) if mouse_speeds else None,
            "std_mouse_speed": round(np.std(mouse_speeds), 2) if mouse_speeds else None,
            "avg_hold_time": round(np.mean(hold_times), 2) if hold_times else None,
            "avg_flight_time": round(np.mean(flight_times), 2) if flight_times else None,
            "rhythm_pattern": {
                "hold_consistency": round(np.std(hold_times) / np.mean(hold_times) if hold_times and np.mean(hold_times)>0 else 0, 4),
                "flight_consistency": round(np.std(flight_times) / np.mean(flight_times) if flight_times and np.mean(flight_times)>0 else 0, 4)
            },
            "session_count": len(sessions),
            "last_updated": datetime.utcnow().isoformat()
        }
        return profile
    
    def detect_anomalous_session(self, current_session: Dict, user_profile: Dict, threshold: float = 2.0) -> Dict[str, Any]:
        """
        Detect if current session deviates significantly from user's historical profile.
        
        Args:
            current_session: Dict with behavioral metrics
            user_profile: Profile from build_profile
            threshold: Z-score threshold for anomaly detection
        
        Returns:
            Dictionary with anomaly flags and deviations
        """
        anomalies = []
        deviation_scores = {}
        
        # Check keystroke speed
        if user_profile.get('avg_keystroke_speed') and current_session.get('typing_speed_cps'):
            avg = user_profile['avg_keystroke_speed']
            std = user_profile.get('std_keystroke_speed', avg * 0.2)
            speed = current_session['typing_speed_cps']
            if std > 0:
                z = abs(speed - avg) / std
                deviation_scores['keystroke_speed'] = z
                if z > threshold:
                    anomalies.append(f"Typing speed deviation: {speed:.1f} cps (expected ~{avg:.1f})")
        
        # Check mouse speed
        if user_profile.get('avg_mouse_speed') and current_session.get('mouse_speed'):
            avg = user_profile['avg_mouse_speed']
            std = user_profile.get('std_mouse_speed', avg * 0.2)
            speed = current_session['mouse_speed']
            if std > 0:
                z = abs(speed - avg) / std
                deviation_scores['mouse_speed'] = z
                if z > threshold:
                    anomalies.append(f"Mouse speed deviation: {speed:.0f} vs baseline {avg:.0f}")
        
        # Check hold time consistency
        if user_profile.get('avg_hold_time') and current_session.get('avg_hold_time'):
            avg = user_profile['avg_hold_time']
            hold = current_session['avg_hold_time']
            if hold > avg * 1.5:
                anomalies.append(f"Hold time unusually long: {hold:.0f}ms (typical {avg:.0f}ms)")
            elif hold < avg * 0.5:
                anomalies.append(f"Hold time unusually short: {hold:.0f}ms (typical {avg:.0f}ms)")
        
        # Overall anomaly score (0-1)
        if deviation_scores:
            max_z = max(deviation_scores.values())
            anomaly_score = min(max_z / (threshold * 2), 1.0)
        else:
            anomaly_score = 0.0
        
        return {
            "is_anomalous": len(anomalies) > 0,
            "anomalies": anomalies,
            "deviation_scores": deviation_scores,
            "anomaly_score": round(anomaly_score, 3)
        }
    
    def add_session_to_history(self, customer_id: str, session_metrics: Dict):
        """Store session metrics for future profiling."""
        self.user_history[customer_id].append({
            "timestamp": datetime.utcnow(),
            "metrics": session_metrics
        })
        # Keep only last 100 sessions
        if len(self.user_history[customer_id]) > 100:
            self.user_history[customer_id] = self.user_history[customer_id][-100:]