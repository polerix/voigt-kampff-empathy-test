"""Configuration loading for the Voight-Kampff test engine."""
import json
import os

DEFAULT_CONFIG = {
    "question_time_limit": 20,
    "sensor_backend": "mock",
    "sensor_poll_interval": 1.0,
    "results_path": "data/results.csv",
    "questions_path": os.path.join(os.path.dirname(__file__), "data", "questions.txt"),
}


def load_config(path=None):
    """Load config from a JSON file, falling back to defaults for missing keys."""
    config = dict(DEFAULT_CONFIG)
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            config.update(json.load(f))
    return config
