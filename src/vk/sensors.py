"""Fake physiological readings for the subject-facing screens.

This is a prop: there is no real CO2/O2/pupil-dilation/reaction-time sensor,
and there won't be - the spec is explicit that fake data is used on purpose.
Values free-run as a plausible random walk. Any field can be pinned to a
fixed value from the puppeteer console (override) for a specific run, and
released back to the random walk (clear_override).
"""
import random
import threading
import time
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class SensorReading:
    co2: float
    o2: float
    pupil_dilation: float  # mm
    pulse: int
    reaction_time: float  # seconds
    elapsed: float


_FIELD_NAMES = {f.name for f in fields(SensorReading)}


def _random_values():
    return {
        "co2": round(random.uniform(300, 1000), 1),
        "o2": round(random.uniform(19.0, 21.0), 2),
        "pupil_dilation": round(random.uniform(2.0, 6.0), 2),
        "pulse": random.randint(55, 110),
        "reaction_time": round(random.uniform(0.3, 2.5), 2),
    }


class SensorHub:
    def __init__(self, poll_interval=1.0):
        self._poll_interval = poll_interval
        self._lock = threading.Lock()
        self._start_time = time.monotonic()
        self._overrides = {}
        self._latest = self._generate()
        self._stop = threading.Event()
        self._thread = None

    def _generate(self):
        values = _random_values()
        values.update(self._overrides)
        values["elapsed"] = time.monotonic() - self._start_time
        return SensorReading(**values)

    def override(self, field, value):
        if field not in _FIELD_NAMES or field == "elapsed":
            raise ValueError(f"unknown sensor field: {field!r}")
        with self._lock:
            self._overrides[field] = value
            self._latest = self._generate()

    def clear_override(self, field):
        with self._lock:
            self._overrides.pop(field, None)

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self._poll_interval * 2)

    def _run(self):
        while not self._stop.is_set():
            with self._lock:
                self._latest = self._generate()
            self._stop.wait(self._poll_interval)

    def snapshot(self):
        with self._lock:
            return self._latest
