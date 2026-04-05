import numpy as np


class KeystrokeDynamics:

    def __init__(self):
        self.keystroke_times = []

    def record_keystroke(self, interval):
        """
        Record time between key presses
        """
        self.keystroke_times.append(interval)

    def average_speed(self):
        if not self.keystroke_times:
            return 0

        return np.mean(self.keystroke_times)

    def detect_anomaly(self):
        """
        Detect abnormal typing behaviour
        """
        avg = self.average_speed()

        if avg > 2.0:
            return True

        return False