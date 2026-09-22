"""Ties sensors, questions, results and the terminal UI into one test run."""
import time

from .input import NonBlockingConsole
from .interface import TerminalUI
from .questions import load_questions
from .results import ResultsLog
from .sensors import SensorHub
from .state import SharedState


class TestSession:
    def __init__(self, config):
        self.config = config
        self.sensors = SensorHub(backend=config["sensor_backend"], poll_interval=config["sensor_poll_interval"])
        self.results = ResultsLog(config["results_path"])
        self.ui = TerminalUI()
        self.questions = load_questions(config["questions_path"])
        self.state = SharedState.instance()

    def run(self):
        self.sensors.start()
        self.state.set_status("running")
        try:
            for question in self.questions:
                self._ask(question)
        finally:
            self.sensors.stop()
            self.state.set_status("idle")

    def _ask(self, question):
        start = time.monotonic()
        response = ""
        with NonBlockingConsole() as console:
            while True:
                elapsed = time.monotonic() - start
                time_left = max(0.0, question.time_limit - elapsed)
                reading = self.sensors.snapshot()
                self.ui.show_question(question, reading, time_left)
                self.state.update(
                    question=question.text,
                    reading=reading,
                    time_left=time_left,
                    time_limit=question.time_limit,
                )
                if time_left <= 0:
                    break
                key = console.get_data()
                if key in ("\r", "\n"):
                    break
                if key:
                    response += key
                time.sleep(0.2)
        self.results.record(question.text, time.monotonic() - start, response)
