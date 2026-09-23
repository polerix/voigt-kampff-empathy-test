"""Ties the fixed question script to an explicit start/pause control.

Earlier versions of this hooked the timer to an "A/V button" toggle, but
A/V recording turned out to be a local subprocess on Tyrell's Pi, outside
the bus entirely - this console can't observe or control it. So the timer
now has its own explicit start()/pause(), driven by a console control, with
wiring it to the real A/V start signal left as a future integration point
if Trevor ever exposes that over the bus.

While running, the current question counts down on its own timer and
auto-advances when it expires; pause() freezes the countdown. There is no
keyboard and no on-screen question text - the agent reads the script from
paper. This module only drives timing, the subject-facing display readout,
and the results log.
"""
import threading
import time

from .questions import load_questions
from .results import ResultsLog


class TestSession:
    def __init__(self, config, sensors, display):
        self.sensors = sensors
        self.display = display
        self.results = ResultsLog(config["results_path"])
        self.questions = load_questions(config["questions_path"])
        self.index = 0
        self.running = False
        self._question_start = time.monotonic()
        self._lock = threading.Lock()
        self._thread = None
        self._stop = threading.Event()

    def start_background(self):
        self.sensors.start()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop_background(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        self.sensors.stop()

    def start(self):
        """Starts (or resumes) the question timer."""
        with self._lock:
            self.running = True
            self._question_start = time.monotonic()
            self._push_display_locked()

    def pause(self):
        """Freezes the question timer where it is."""
        with self._lock:
            self.running = False

    def jump_to(self, index):
        """Service-mode override to jump to a specific question."""
        with self._lock:
            self.index = max(0, min(len(self.questions) - 1, index))
            self._question_start = time.monotonic()
            self._push_display_locked()

    def set_deviation(self, value):
        self.display.set_deviation(value)

    def _push_display_locked(self):
        question = self.questions[self.index]
        reading = self.sensors.snapshot()
        self.display.start_question(self.index, question.expected_response, reading.__dict__)

    def _run(self):
        while not self._stop.is_set():
            with self._lock:
                running = self.running
                index = self.index
                elapsed = time.monotonic() - self._question_start
            if running:
                reading = self.sensors.snapshot()
                self.display.update_sensors(reading.__dict__)
                question = self.questions[index]
                if elapsed >= question.time_limit:
                    self.results.record(
                        question_index=index,
                        expected_response=question.expected_response,
                        deviation=self.display.snapshot()["deviation"],
                        sensors=reading.__dict__,
                        duration=elapsed,
                    )
                    with self._lock:
                        self.index = (index + 1) % len(self.questions)
                        self._question_start = time.monotonic()
                        self._push_display_locked()
            time.sleep(0.2)
