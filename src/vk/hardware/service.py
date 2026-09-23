"""Service-mode operations, gated by the service token (distinct from the
normal operator token): GPIO diagnostics and motion/timing calibration.
Real diagnostics are stubbed pending actual hardware to test against.
"""


class PermissionDenied(Exception):
    pass


class ServicePanel:
    def __init__(self, controller, questions):
        self.controller = controller
        self.questions = questions

    def _require_service_role(self):
        if self.controller.tokens.role() != "service":
            raise PermissionDenied("service token required")

    def check_gpio(self):
        self._require_service_role()
        if self.controller.arm.backend == "mock":
            return {"arm": "mock-ok", "bellows": "mock-ok", "av": "mock-ok", "tokens": "mock-ok"}
        raise NotImplementedError("real GPIO diagnostics not wired up yet")

    def calibrate_motion(self, actuator, **params):
        self._require_service_role()
        raise NotImplementedError("motion calibration not wired up yet - no real actuator hardware")

    def set_question_time_limit(self, index, seconds):
        self._require_service_role()
        self.questions[index].time_limit = int(seconds)
        return self.questions[index]
