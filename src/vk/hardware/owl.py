"""Owl (master) command surfaces: the two OLEDs plus the HDMI, its sfx
vocabulary, and screen navigation. Addressed over the bus per
docs/design/mqtt-contract.md.

Owl has no reply topic - per the contract, its command confirmations are
pushed straight into its own local console, not back over the bus. So this
side tracks "last commanded" values, not confirmed state, for everything
except vk/state and vk/glitch, which Owl does broadcast (see bus.py).
"""

SFX_EVENTS = ["button", "function", "iris", "screen", "bellows_on", "bellows_off", "static_on", "static_off"]
SFX_BUTTON_ALIASES = ["button1", "button2", "button3"]

SCREEN_CTL_PAYLOADS = [
    "all_black",
    "all_static",
    "a_home",
    "a_next",
    "a_prev",
    "b_home",
    "b_next",
    "b_prev",
    "main_home",
    "main_next",
    "main_prev",
    "main_vkos",
    "vkos_next",
    "vkos_prev",
    "vkos_auto_on",
    "vkos_auto_off",
    "main_quiz_start",
    "main_quiz_next",
    "main_quiz_prev",
    "main_quiz_scroll_up",
    "main_quiz_scroll_down",
    "main_video_start",
    "main_video_next",
    "main_video_prev",
]

_FX_KNOBS = {"displayA": ["teeth", "spike", "tilt", "pulse"], "displayB": ["shape", "tuck", "pulse"]}


class OwlDisplay:
    """One of displayA (OLED), displayB (OLED), or displayM (HDMI). Only A
    and B have FX knobs - M is static/roll only."""

    def __init__(self, bus, name):
        if name not in ("displayA", "displayB", "displayM"):
            raise ValueError(f"unknown display: {name!r}")
        self._bus = bus
        self.name = name
        self.static_level = 0
        self.roll_level = 0
        self.fx = dict.fromkeys(_FX_KNOBS.get(name, []), 0)

    @staticmethod
    def _clamp(value):
        return max(0, min(100, int(value)))

    def set_static(self, value):
        value = self._clamp(value)
        self._bus.publish(f"vk/owl/{self.name}/static", value)
        self.static_level = value

    def set_roll(self, value):
        value = self._clamp(value)
        self._bus.publish(f"vk/owl/{self.name}/roll", value)
        self.roll_level = value

    def set_fx(self, knob, value):
        if knob not in self.fx:
            raise ValueError(f"{self.name} has no fx knob {knob!r}")
        value = self._clamp(value)
        self._bus.publish(f"vk/owl/{self.name}/fx/{knob}", value)
        self.fx[knob] = value


class Owl:
    def __init__(self, bus):
        self._bus = bus
        self.display_a = OwlDisplay(bus, "displayA")
        self.display_b = OwlDisplay(bus, "displayB")
        self.display_m = OwlDisplay(bus, "displayM")

    def fx_reset(self):
        self._bus.publish("vk/owl/fx/reset", 1)
        for display in (self.display_a, self.display_b):
            for knob in display.fx:
                display.fx[knob] = 0

    def sfx(self, event):
        if event not in SFX_EVENTS and event not in SFX_BUTTON_ALIASES:
            raise ValueError(f"unknown sfx event: {event!r}")
        self._bus.publish("vk/owl/sfx", event)

    def screen_ctl(self, payload):
        if payload not in SCREEN_CTL_PAYLOADS:
            raise ValueError(f"unknown screen_ctl payload: {payload!r}")
        self._bus.publish("vk/owl/screen_ctl", payload)

    def displays(self):
        return {"displayA": self.display_a, "displayB": self.display_b, "displayM": self.display_m}

    def snapshot(self):
        return {
            name: {"static": d.static_level, "roll": d.roll_level, "fx": dict(d.fx)}
            for name, d in self.displays().items()
        }
