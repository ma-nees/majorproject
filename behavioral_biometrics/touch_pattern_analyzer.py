import numpy as np


class TouchPatternAnalyzer:

    def __init__(self):
        self.pressure_values = []

    def record_touch(self, pressure):

        self.pressure_values.append(pressure)

    def average_pressure(self):

        if not self.pressure_values:
            return 0

        return np.mean(self.pressure_values)

    def detect_unusual_touch(self):

        avg = self.average_pressure()

        if avg < 0.2:
            return True

        return False