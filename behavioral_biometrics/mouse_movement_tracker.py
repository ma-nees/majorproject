import numpy as np


class MouseMovementTracker:

    def __init__(self):
        self.movements = []

    def record_movement(self, distance):
        """
        Record mouse movement distance
        """
        self.movements.append(distance)

    def movement_variance(self):

        if not self.movements:
            return 0

        return np.var(self.movements)

    def detect_bot_behavior(self):

        variance = self.movement_variance()

        if variance < 1:
            return True

        return False