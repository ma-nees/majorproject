"""
Behavior Monitor Module

This module monitors user behavioral patterns during a transaction
session and detects anomalies using behavioral metrics.

It works together with:
- behavioral biometrics
- anomaly detection
- risk engine
"""

import time
import numpy as np


class BehaviorMonitor:

    def __init__(self):
        self.session_data = []

    def record_event(self, event_type, value):
        """
        Record behavioral events such as keystrokes,
        mouse movement speed, or touch pressure.
        """

        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "value": value
        }

        self.session_data.append(event)

    def get_session_duration(self):
        """
        Calculate session duration
        """

        if len(self.session_data) < 2:
            return 0

        start = self.session_data[0]["timestamp"]
        end = self.session_data[-1]["timestamp"]

        return end - start

    def compute_behavior_features(self):
        """
        Convert session data into numerical features
        used by anomaly detection models
        """

        values = [event["value"] for event in self.session_data]

        if not values:
            return {
                "mean_value": 0,
                "std_value": 0,
                "event_count": 0,
                "session_duration": 0
            }

        features = {
            "mean_value": float(np.mean(values)),
            "std_value": float(np.std(values)),
            "event_count": len(values),
            "session_duration": self.get_session_duration()
        }

        return features

    def detect_abnormal_behavior(self):
        """
        Basic rule-based abnormal behavior detection
        """

        features = self.compute_behavior_features()

        if features["event_count"] > 100:
            return True

        if features["std_value"] > 50:
            return True

        if features["session_duration"] < 1:
            return True

        return False

    def reset_session(self):
        """
        Reset monitoring session
        """
        self.session_data = []


# Example test
if __name__ == "__main__":

    monitor = BehaviorMonitor()

    monitor.record_event("mouse_move", 12)
    monitor.record_event("mouse_move", 18)
    monitor.record_event("keystroke", 22)

    print("Session duration:", monitor.get_session_duration())

    features = monitor.compute_behavior_features()
    print("Behavior Features:", features)

    abnormal = monitor.detect_abnormal_behavior()
    print("Abnormal behavior detected:", abnormal)