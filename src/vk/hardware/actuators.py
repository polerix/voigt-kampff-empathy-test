"""Tyrell (worker) command surfaces, addressed over the bus per
docs/design/mqtt-contract.md. Identical whether the bus is mock or real -
these classes only ever call bus.publish(); they don't know or care which
backend is underneath.

A/V recording is deliberately NOT here as an MQTT-addressable action: it's
a local camera/mic subprocess that Tyrell shells out to directly, outside
the bus entirely. AVRecorder stays a software-only concept for the
mock/test-software site; in real mode there is nothing on the bus to call.
"""

ARM_ACTIONS = ["raise", "lower", "home", "abort", "boothome-on", "boothome-off", "sethome", "forget", "state"]


class Arm:
    """The macro-level `vk/tyrell/arm` topic, plus the three independently
    addressable joints. There is no single "raised" boolean on the real
    device - shoulder/elbow/wrist each move on their own command, and
    Tyrell tracks homing/calibration state itself (see tyrell_state.json
    in BladeRunnerVK - not mirrored here, this console doesn't own it)."""

    def __init__(self, bus):
        self._bus = bus

    def command(self, action):
        if action not in ARM_ACTIONS:
            raise ValueError(f"unknown arm action: {action!r}")
        self._bus.publish("vk/tyrell/arm", action)

    def shoulder(self, action):
        if action not in ("extend", "retract"):
            raise ValueError(f"unknown shoulder action: {action!r}")
        self._bus.publish("vk/tyrell/shoulder", action)

    def elbow(self, action):
        if action not in ("extend", "retract", "stop"):
            raise ValueError(f"unknown elbow action: {action!r}")
        self._bus.publish("vk/tyrell/elbow", action)

    def wrist(self, action):
        if action not in ("extend", "retract"):
            raise ValueError(f"unknown wrist action: {action!r}")
        self._bus.publish("vk/tyrell/wrist", action)


class Bellows:
    def __init__(self, bus):
        self._bus = bus

    def on(self):
        self._bus.publish("vk/tyrell/bellows", "on")

    def off(self):
        self._bus.publish("vk/tyrell/bellows", "off")


class Worker:
    """`vk/tyrell/worker` - a macro that expands into arm + bellows commands
    on Tyrell's side. This is the closest real equivalent to "press the
    button that runs the whole physical performance"."""

    def __init__(self, bus):
        self._bus = bus

    def start(self):
        self._bus.publish("vk/tyrell/worker", "start")

    def stop(self):
        self._bus.publish("vk/tyrell/worker", "stop")


class Leds:
    def __init__(self, bus):
        self._bus = bus

    def _command(self, payload):
        self._bus.publish("vk/tyrell/leds", payload)

    def eye(self, on):
        self._command("eye_on" if on else "eye_off")

    def buttons(self, on):
        self._command("buttons_on" if on else "buttons_off")

    def buttons_boot(self):
        self._command("buttons_boot")

    def movie(self, on):
        self._command("movie_on" if on else "movie_off")

    def vus(self, on):
        self._command("vus_on" if on else "vus_off")


class AVRecorder:
    """Not on the bus. Tyrell shells out to a local camera/mic process for
    this; the real backend has nothing to call until/unless that gets
    exposed over MQTT. The mock backend simulates it for the
    test-software site."""

    def __init__(self, backend="mock"):
        self.backend = backend
        self.recording = False

    def start(self):
        if self.backend == "real":
            raise NotImplementedError(
                "A/V recording is a local subprocess on Tyrell's Pi, outside the bus - not controllable from here yet"
            )
        self.recording = True

    def stop(self):
        if self.backend == "real":
            raise NotImplementedError(
                "A/V recording is a local subprocess on Tyrell's Pi, outside the bus - not controllable from here yet"
            )
        self.recording = False
