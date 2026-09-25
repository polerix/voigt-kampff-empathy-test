"""Interview-layer readout state: what the /display/<n> kiosk pages show.

This is a separate concern from hardware/owl.py's real OLED/HDMI control -
it's this application's own simulation of "expected response / deviation /
fake biometrics" for the empathy-test screens, not yet wired to Owl's real
displays. Whether/how those should eventually be the same thing (e.g. via
Owl's main_quiz_* screen_ctl mode) is still open - see docs/design/device.md.
"""
import threading


class DisplayState:
    def __init__(self):
        self._lock = threading.Lock()
        self._booted = False
        self._mode = "boot"  # boot | standby | testing
        self._question_index = None
        self._expected_response = None
        self._deviation = 0.0  # 0-100, set by the operator via the console
        self._sensors = None

    def set_booted(self, booted=True):
        with self._lock:
            self._booted = booted
            self._mode = "standby" if booted else "boot"

    def start_question(self, index, expected_response, sensors):
        with self._lock:
            self._mode = "testing"
            self._question_index = index
            self._expected_response = expected_response
            self._sensors = sensors

    def update_sensors(self, sensors):
        with self._lock:
            self._sensors = sensors

    def set_deviation(self, value):
        with self._lock:
            self._deviation = max(0.0, min(100.0, value))

    def clear_question(self):
        with self._lock:
            self._mode = "standby"
            self._question_index = None
            self._expected_response = None

    def snapshot(self):
        with self._lock:
            return {
                "booted": self._booted,
                "mode": self._mode,
                "question_index": self._question_index,
                "expected_response": self._expected_response,
                "deviation": self._deviation,
                "sensors": self._sensors,
            }
