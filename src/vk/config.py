"""Configuration for the Voight-Kampff test engine.

hardware_backend is the one global switch: "mock" runs the whole stack with
no prop attached (the "test the software" site), "real" drives the actual
GPIO/i2c/HDMI hardware (the "puppeteer the prop" site) using the same code.
token_backend only matters when hardware_backend is "real" - it picks which
physical reader the token drawer uses.
"""
import json
import os

DEFAULT_CONFIG = {
    "hardware_backend": "mock",  # "mock" | "real"
    "token_backend": "mock",  # "mock" | "rfid" | "magnetic" (real reader hardware)
    # Maps a token's id (as read by the real reader, or a string you type into
    # the mock console) to its role. Fill in with real token ids once you have
    # readers wired up.
    "token_roles": {
        "OPERATOR-1": "operator",
        "SERVICE-1": "service",
    },
    "enforce_button_sequence": True,  # arm -> bellows -> av; see hardware/buttons.py
    "sounds_directory": os.path.join(os.path.dirname(__file__), "..", "..", "sounds"),
    "results_path": "data/results.csv",
    "questions_path": os.path.join(os.path.dirname(__file__), "data", "questions.csv"),
    "sensor_poll_interval": 1.0,
    "gpio_pins": {
        # TODO: fill in real BCM pin numbers once the prop's wiring is known.
        # Not read by anything yet - the "real" hardware backends are stubs
        # that raise NotImplementedError until this is wired up.
        "button_arm": None,
        "button_bellows": None,
        "button_av": None,
        "led_arm": None,
        "led_bellows": None,
        "led_av": None,
        "arm_motor": None,
        "bellows_relay": None,
        "camera_focus": None,
    },
}


def load_config(path=None):
    """Load config from a JSON file, falling back to defaults for missing keys."""
    config = dict(DEFAULT_CONFIG)
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            config.update(json.load(f))
    return config
