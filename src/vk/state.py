"""In-memory state shared between a running test session and the web dashboard."""
import threading


class SharedState:
    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._status = "idle"
        self._question = None
        self._reading = None
        self._time_left = None
        self._time_limit = None

    @classmethod
    def instance(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def set_status(self, status):
        with self._lock:
            self._status = status

    def update(self, question, reading, time_left, time_limit):
        with self._lock:
            self._question = question
            self._reading = reading
            self._time_left = time_left
            self._time_limit = time_limit

    def snapshot(self):
        with self._lock:
            reading = self._reading
            return {
                "status": self._status,
                "question": self._question,
                "time_left": round(self._time_left, 1) if self._time_left is not None else None,
                "time_limit": self._time_limit,
                "sensors": (
                    {
                        "co2": reading.co2,
                        "o2": reading.o2,
                        "iris": reading.iris,
                        "pulse": reading.pulse,
                        "elapsed": round(reading.elapsed, 1),
                    }
                    if reading
                    else None
                ),
            }
