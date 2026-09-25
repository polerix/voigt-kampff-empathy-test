"""Configuration for the Voight-Kampff web console.

hardware_backend picks the bus implementation: "mock" talks to nothing (the
"test the software" site), "real" connects to the actual VK prop's MQTT
broker (the "puppeteer the prop" site) - see docs/design/mqtt-contract.md.
Both backends expose the identical Arm/Bellows/Worker/Leds/Owl command
surfaces; only what's underneath differs.
"""
import json
import os

DEFAULT_CONFIG = {
    "hardware_backend": "mock",  # "mock" | "real"
    "mqtt_host": "owl.local",
    "mqtt_port": 1883,
    "mqtt_client_id": "vk-web-console",
    "mqtt_reply_timeout": 1.5,  # seconds; matches Tyrell's own "(no reply)" timeout
    "token_backend": "mock",  # "mock" | "rfid" | "magnetic"
    # Console-side safety gate only - Trevor's Tyrell/Owl code does not check
    # or enforce this itself yet, so this never blocks a real command at the
    # device. It exists so the console UI doesn't let someone poke the real
    # arm/bellows without deliberately "unlocking" it first.
    "token_roles": {
        "OPERATOR-1": "operator",
        "SERVICE-1": "service",
    },
    "results_path": "data/results.csv",
    "questions_path": os.path.join(os.path.dirname(__file__), "data", "questions.csv"),
    "sensor_poll_interval": 1.0,
}


def load_config(path=None):
    """Load config from a JSON file, falling back to defaults for missing keys."""
    config = dict(DEFAULT_CONFIG)
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            config.update(json.load(f))
    return config
