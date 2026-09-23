"""The three square white control buttons: camera arm, pheromone bellows,
A/V recording.

Each button toggles its mechanism between active and suspended; its LED
lights only while a security token is present. Pressing plays an
activation or suspension sound cue.

ASSUMPTION: the spec describes using the buttons "sequentially" (arm, then
bellows, then A/V). This is read as an enforced interlock - a button won't
activate until the ones before it in BUTTON_ORDER are active - not just a
description of typical use. Set enforce_sequence=False in config if that
reading is wrong.
"""
from dataclasses import dataclass

BUTTON_ORDER = ["arm", "bellows", "av"]


@dataclass
class ButtonState:
    active: bool = False


class ButtonPanel:
    def __init__(self, security, sounds, enforce_sequence=True):
        self.security = security
        self.sounds = sounds
        self.enforce_sequence = enforce_sequence
        self._buttons = {name: ButtonState() for name in BUTTON_ORDER}
        self._on_toggle = {}  # name -> callback(active: bool)

    def on_toggle(self, name, callback):
        """Registers callback(active: bool), invoked whenever `name` toggles."""
        self._on_toggle[name] = callback

    def led_on(self, name):
        return self.security.role() != "locked" and self._buttons[name].active

    def press(self, name):
        """Returns (ok, reason); ok=False means the press was rejected."""
        if name not in self._buttons:
            raise ValueError(f"unknown button: {name}")
        if self.security.role() == "locked":
            return False, "no security token present"
        state = self._buttons[name]
        if self.enforce_sequence and not state.active:
            index = BUTTON_ORDER.index(name)
            for earlier in BUTTON_ORDER[:index]:
                if not self._buttons[earlier].active:
                    return False, f"{earlier} must be active before {name}"
        state.active = not state.active
        self.sounds.play("button_activate" if state.active else "button_suspend")
        callback = self._on_toggle.get(name)
        if callback:
            callback(state.active)
        return True, "activated" if state.active else "suspended"

    def snapshot(self):
        return {name: {"active": s.active, "led": self.led_on(name)} for name, s in self._buttons.items()}
