"""Shared state for the three subject-facing screens.

The screens never show question text (the agent reads the script from
paper) and take no input. They boot through a status/accreditation
sequence, then during a test show the fake physiological readout plus the
operator-set expected-response reference and deviation level.
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
