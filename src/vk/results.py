"""Persists one CSV row per answered question: the expected-response
reference, the deviation level the operator puppeteered, the fake sensor
snapshot at that moment, and how long the question ran.
"""
import csv
import datetime
import os
from dataclasses import asdict, dataclass


@dataclass
class ResultRecord:
    timestamp: str
    question_index: int
    expected_response: str
    deviation: float
    co2: float
    o2: float
    pupil_dilation: float
    pulse: int
    reaction_time: float
    duration: float


class ResultsLog:
    FIELDNAMES = list(ResultRecord.__dataclass_fields__.keys())

    def __init__(self, path):
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.isfile(path):
            with open(path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=self.FIELDNAMES).writeheader()

    def record(self, question_index, expected_response, deviation, sensors, duration):
        entry = ResultRecord(
            timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
            question_index=question_index,
            expected_response=expected_response,
            deviation=round(deviation, 1),
            co2=sensors["co2"],
            o2=sensors["o2"],
            pupil_dilation=sensors["pupil_dilation"],
            pulse=sensors["pulse"],
            reaction_time=sensors["reaction_time"],
            duration=round(duration, 2),
        )
        with open(self.path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=self.FIELDNAMES).writerow(asdict(entry))
        return entry

    def all(self):
        if not os.path.isfile(self.path):
            return []
        with open(self.path, newline="") as f:
            return list(csv.DictReader(f))
