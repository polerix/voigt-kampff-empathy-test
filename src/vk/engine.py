"""Ties the fixed question script to the A/V button.

While A/V is active, the current question counts down on its own timer and
auto-advances when it expires; the A/V button pauses/resumes that
countdown. There is no keyboard and no on-screen question text - the agent
reads the script from paper. This module only drives timing, the
subject-facing display readout, the stimulus-tone cue at each boundary, and
the results log.
"""
import threading
import time

from .questions import load_questions
from .results import ResultsLog


class TestSession:
    def __init__(self, config, hardware, sensors):
        self.hardware = hardware
        self.sensors = sensors
        self.results = ResultsLog(config["results_path"])
        self.questions = load_questions(config["questions_path"])
        self.index = 0
        self.running = False
        self._question_start = time.monotonic()
        self._lock = threading.Lock()
        self._thread = None
        self._stop = threading.Event()
        self.hardware.on_av_toggle(self._on_av_toggle)

    def start(self):
        self.sensors.start()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        self.sensors.stop()

    def _on_av_toggle(self, active):
        with self._lock:
            self.running = active
            if active:
                self._question_start = time.monotonic()
                self._push_display_locked()

    def jump_to(self, index):
        """Service-mode override to jump to a specific question."""
        with self._lock:
            self.index = max(0, min(len(self.questions) - 1, index))
            self._question_start = time.monotonic()
            self._push_display_locked()

    def set_deviation(self, value):
        self.hardware.displays.set_deviation(value)

    def _push_display_locked(self):
        question = self.questions[self.index]
        reading = self.sensors.snapshot()
        self.hardware.displays.start_question(self.index, question.expected_response, reading.__dict__)

    def _run(self):
        while not self._stop.is_set():
            with self._lock:
                running = self.running
                index = self.index
                elapsed = time.monotonic() - self._question_start
            if running:
                reading = self.sensors.snapshot()
                self.hardware.displays.update_sensors(reading.__dict__)
                question = self.questions[index]
                if elapsed >= question.time_limit:
                    self.results.record(
                        question_index=index,
                        expected_response=question.expected_response,
                        deviation=self.hardware.displays.snapshot()["deviation"],
                        sensors=reading.__dict__,
                        duration=elapsed,
                    )
                    self.hardware.sounds.play("stimulus_tone")
                    with self._lock:
                        self.index = (index + 1) % len(self.questions)
                        self._question_start = time.monotonic()
                        self._push_display_locked()
            time.sleep(0.2)
