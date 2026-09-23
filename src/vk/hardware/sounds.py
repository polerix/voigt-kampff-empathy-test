"""Sound cue playback: button activation/suspension, a deviation alert, and
a timed-stimulus tone at each question boundary.

The mock backend just logs what would have played (and keeps a short
history the test-software site can display). The real backend looks for
<event>.wav under the configured sounds directory and plays it with aplay;
a missing file logs a warning instead of failing the run. No audio files
are checked into this repo - see sounds/README.md.
"""
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

EVENTS = [
    "button_activate",
    "button_suspend",
    "deviation_alert",
    "stimulus_tone",
]


class SoundPlayer:
    def __init__(self, backend="mock", directory="sounds"):
        self.backend = backend
        self.directory = directory
        self.log = []  # mock backend only: history of events played

    def play(self, event):
        if event not in EVENTS:
            raise ValueError(f"unknown sound event: {event!r}")
        if self.backend == "mock":
            self.log.append(event)
            logger.info("mock sound: %s", event)
            return
        path = os.path.join(self.directory, f"{event}.wav")
        if not os.path.isfile(path):
            logger.warning("sound file missing, skipping playback: %s", path)
            return
        subprocess.Popen(["aplay", "-q", path])
