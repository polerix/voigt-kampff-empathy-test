"""Composes the bus and the Tyrell/Owl command surfaces built on it.

hardware_backend picks the bus only (MockBus or VKBus) - Arm/Bellows/
Worker/Leds/Owl are identical either way; they just publish through a bus
that logs locally or one that's actually talking to owl.local.
"""
from .actuators import AVRecorder, Arm, Bellows, Worker, Leds
from .bus import MockBus, VKBus
from .owl import Owl
from .tokens import TokenReader


class HardwareController:
    def __init__(self, config):
        backend = config["hardware_backend"]
        if backend == "mock":
            self.bus = MockBus()
        elif backend == "real":
            self.bus = VKBus(
                host=config["mqtt_host"],
                port=config["mqtt_port"],
                client_id=config["mqtt_client_id"],
                reply_timeout=config["mqtt_reply_timeout"],
            )
        else:
            raise ValueError(f"unknown hardware_backend: {backend!r}")
        self.bus.connect()

        self.tokens = TokenReader(backend=config["token_backend"], roles=config["token_roles"])
        self.arm = Arm(self.bus)
        self.bellows = Bellows(self.bus)
        self.worker = Worker(self.bus)
        self.leds = Leds(self.bus)
        self.owl = Owl(self.bus)
        self.av = AVRecorder(backend=backend)

    def snapshot(self):
        return {
            "security_role": self.tokens.role(),
            "bus": self.bus.snapshot(),
            "owl": self.owl.snapshot(),
            "av_recording": self.av.recording,
            # Optimistic (last-commanded, not confirmed) - see actuators.py.
            "arm": {"last_action": self.arm.last_action, "joints": dict(self.arm.joint_state)},
            "bellows_running": self.bellows.running,
            "leds": dict(self.leds.state),
        }
