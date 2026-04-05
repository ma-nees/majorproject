class BehavioralRiskScore:

    def __init__(self):
        self.score = 0

    def calculate(self, analysis):

        score = 0

        if analysis["keystroke_anomaly"]:
            score += 30

        if analysis["mouse_anomaly"]:
            score += 30

        if analysis["touch_anomaly"]:
            score += 40

        return score