"""The fixed question script.

The questions are always the same, in the same order - there is no
randomization and no on-screen question text. The human agent reads each
question aloud from a paper copy of this same script; the software only
needs the timing and the expected-response reference shown on the
subject-facing screens.

expected_response is calibration data (what a non-deviating answer looks
like) that belongs to the physical test, not something this codebase can
invent - rows ship with it blank. Fill in data/questions.csv directly.
"""
import csv
from dataclasses import dataclass

DEFAULT_TIME_LIMIT = 20


@dataclass
class Question:
    text: str
    time_limit: int  # seconds before auto-advancing to the next question
    expected_response: str = ""


def load_questions(path):
    questions = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("text", "").strip():
                continue
            time_limit = int(row["time_limit"]) if row.get("time_limit") else DEFAULT_TIME_LIMIT
            questions.append(
                Question(
                    text=row["text"].strip(),
                    time_limit=time_limit,
                    expected_response=(row.get("expected_response") or "").strip(),
                )
            )
    return questions
