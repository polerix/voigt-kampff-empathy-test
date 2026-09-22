"""Question bank loading for the Voight-Kampff empathy test."""
import re
from dataclasses import dataclass

_LINE_RE = re.compile(r"^(?P<text>.*?)\{(?P<minutes>\d{1,2}):(?P<seconds>\d{2})\}\s*,?\s*$")

DEFAULT_TIME_LIMIT = 20


@dataclass
class Question:
    text: str
    time_limit: int  # seconds allotted to answer


def load_questions(path):
    """Parse a questions file where each line is '<question text>{MM:SS}'."""
    questions = []
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            match = _LINE_RE.match(line)
            if match:
                minutes = int(match.group("minutes"))
                seconds = int(match.group("seconds"))
                questions.append(Question(text=match.group("text").strip(), time_limit=minutes * 60 + seconds))
            else:
                questions.append(Question(text=line, time_limit=DEFAULT_TIME_LIMIT))
    return questions
