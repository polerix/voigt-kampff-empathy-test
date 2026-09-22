"""Persists Voight-Kampff test results as CSV, one row per answered question."""
import csv
import datetime
import os
from dataclasses import asdict, dataclass


@dataclass
class ResultRecord:
    timestamp: str
    question: str
    time_taken: float
    response: str
    verdict: str


class ResultsLog:
    FIELDNAMES = ["timestamp", "question", "time_taken", "response", "verdict"]

    def __init__(self, path):
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.isfile(path):
            with open(path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=self.FIELDNAMES).writeheader()

    def record(self, question, time_taken, response, verdict="pending"):
        entry = ResultRecord(
            timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
            question=question,
            time_taken=round(time_taken, 2),
            response=response,
            verdict=verdict,
        )
        with open(self.path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=self.FIELDNAMES).writerow(asdict(entry))
        return entry

    def all(self):
        if not os.path.isfile(self.path):
            return []
        with open(self.path, newline="") as f:
            return list(csv.DictReader(f))
