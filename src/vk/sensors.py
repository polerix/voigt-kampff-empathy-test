"""Sensor readings for the Voight-Kampff test rig.

Runs a background poll loop and exposes the latest reading as a thread-safe
snapshot. The "mock" backend generates plausible random values so the engine
and web dashboard work without hardware attached. A real backend (GPIO/I2C
sensors, an eye-tracking webcam) can be added later by implementing a new
read function with the same signature and registering it in BACKENDS.
"""
import random
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    co2: float
    o2: float
    iris: str
    pulse: int
    elapsed: float


def _read_mock():
    return SensorReading(
        co2=round(random.uniform(0.0, 1.0) * 1000, 2),
        o2=round(random.uniform(0.0, 1.0) * 100, 2),
        iris=random.choice(["green", "blue", "brown", "hazel"]),
        pulse=random.randint(55, 110),
        elapsed=0.0,
    )


BACKENDS = {"mock": _read_mock}


class SensorHub:
    """Polls a sensor backend on a background thread and holds the latest reading."""

    def __init__(self, backend="mock", poll_interval=1.0):
        if backend not in BACKENDS:
            raise ValueError(f"unknown sensor backend: {backend!r}")
        self._read = BACKENDS[backend]
        self._poll_interval = poll_interval
        self._lock = threading.Lock()
        self._start_time = time.monotonic()
        self._latest = self._with_elapsed(self._read())
        self._stop = threading.Event()
        self._thread = None

    def _with_elapsed(self, reading):
        return SensorReading(
            co2=reading.co2,
            o2=reading.o2,
            iris=reading.iris,
            pulse=reading.pulse,
            elapsed=time.monotonic() - self._start_time,
        )

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
                self._latest = self._with_elapsed(self._read())
            self._stop.wait(self._poll_interval)

    def snapshot(self):
        with self._lock:
            return self._latest
