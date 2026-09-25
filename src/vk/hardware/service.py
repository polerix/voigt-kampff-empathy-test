"""Service-mode operations, gated by the service token (console-side only -
see tokens.py). There's no GPIO in this repo to diagnose anymore - the
integration boundary is the bus - so the one real diagnostic is "can we
see Tyrell." Motion/timing calibration lives on Tyrell itself (arm
sethome/forget, already exposed directly via Arm) rather than here.
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

    def check_bus(self):
        self._require_service_role()
        return self.controller.bus.snapshot()

    def set_question_time_limit(self, index, seconds):
        self._require_service_role()
        self.questions[index].time_limit = int(seconds)
        return self.questions[index]
