"""Single facade over all hardware: tokens, buttons, actuators, sounds,
displays. Built once per process from config. hardware_backend is one
global switch so the same code runs with no prop attached or against the
real Pi (GPIO/i2c/HDMI).
"""
from .actuators import AVRecorder, Bellows, CameraArm
from .buttons import ButtonPanel
from .displays import DisplayState
from .sounds import SoundPlayer
from .tokens import TokenReader


class HardwareController:
    def __init__(self, config):
        backend = config["hardware_backend"]
        self.tokens = TokenReader(backend=config["token_backend"], roles=config["token_roles"])
        self.sounds = SoundPlayer(backend=backend, directory=config["sounds_directory"])
        self.arm = CameraArm(backend=backend)
        self.bellows = Bellows(backend=backend)
        self.av = AVRecorder(backend=backend)
        self.buttons = ButtonPanel(self.tokens, self.sounds, enforce_sequence=config["enforce_button_sequence"])
        self.displays = DisplayState()

        self._av_toggle_callback = None  # engine.py hooks in here to run/pause the question timer
        self.buttons.on_toggle("arm", lambda active: self.arm.raise_() if active else self.arm.lower())
        self.buttons.on_toggle("bellows", lambda active: self.bellows.start() if active else self.bellows.stop())
        self.buttons.on_toggle("av", self._on_av_toggle)

    def on_av_toggle(self, callback):
        self._av_toggle_callback = callback

    def _on_av_toggle(self, active):
        if active:
            self.av.start()
        else:
            self.av.stop()
        if self._av_toggle_callback:
            self._av_toggle_callback(active)

    def snapshot(self):
        return {
            "security_role": self.tokens.role(),
            "buttons": self.buttons.snapshot(),
            "arm_raised": self.arm.raised,
            "bellows_running": self.bellows.running,
            "av_recording": self.av.recording,
            "display": self.displays.snapshot(),
        }
