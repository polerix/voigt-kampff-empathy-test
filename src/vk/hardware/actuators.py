"""Physical actuators driven by the button panel: the camera arm (plus its
own manual focus button), the pheromone bellows fan, and the A/V recorder.
The "real" backend for each is a documented stub pending real pin/wiring
info - nothing here has hardware to test against yet.
"""


class CameraArm:
    def __init__(self, backend="mock"):
        self.backend = backend
        self.raised = False

    def raise_(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the arm motor pin in config.gpio_pins")
        self.raised = True

    def lower(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the arm motor pin in config.gpio_pins")
        self.raised = False

    def focus_pulse(self):
        """The manual focus button on the camera itself - separate from the
        3 panel buttons, works regardless of security role."""
        if self.backend == "real":
            raise NotImplementedError("wire up the camera focus signal in config.gpio_pins")
        return True


class Bellows:
    def __init__(self, backend="mock"):
        self.backend = backend
        self.running = False

    def start(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the bellows relay pin in config.gpio_pins")
        self.running = True

    def stop(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the bellows relay pin in config.gpio_pins")
        self.running = False


class AVRecorder:
    def __init__(self, backend="mock"):
        self.backend = backend
        self.recording = False

    def start(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the camera/mic capture pipeline")
        self.recording = True

    def stop(self):
        if self.backend == "real":
            raise NotImplementedError("wire up the camera/mic capture pipeline")
        self.recording = False
