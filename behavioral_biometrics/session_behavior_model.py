from behavioral_biometrics.keystroke_dynamics import KeystrokeDynamics
from behavioral_biometrics.mouse_movement_tracker import MouseMovementTracker
from behavioral_biometrics.touch_pattern_analyzer import TouchPatternAnalyzer


class SessionBehaviorModel:

    def __init__(self):

        self.keystroke = KeystrokeDynamics()
        self.mouse = MouseMovementTracker()
        self.touch = TouchPatternAnalyzer()

    def record_behavior(self, keystroke, mouse_move, touch_pressure):

        self.keystroke.record_keystroke(keystroke)
        self.mouse.record_movement(mouse_move)
        self.touch.record_touch(touch_pressure)

    def analyze_session(self):

        keystroke_flag = self.keystroke.detect_anomaly()
        mouse_flag = self.mouse.detect_bot_behavior()
        touch_flag = self.touch.detect_unusual_touch()

        return {
            "keystroke_anomaly": keystroke_flag,
            "mouse_anomaly": mouse_flag,
            "touch_anomaly": touch_flag
        }