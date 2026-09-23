"""Console-side security gate for the token drawer.

This is NOT enforced by the real device: Trevor hasn't integrated the
drawer token into Tyrell/Owl at all yet, so a "real" command still reaches
the prop regardless of what this reports. It exists purely so the web
console itself doesn't let someone poke the real arm/bellows without
deliberately "unlocking" it first - a software seatbelt, not a hardware
one. Once/if drawer detection lands on the device side, wire a real
backend in here to match it.

  no token         -> "locked"   (console UI keeps controls disabled)
  operator token   -> "operator" (normal console use)
  service token    -> "service"  (bus diagnostics, question-script overrides)
"""
import threading


class _MockTokenBackend:
    def __init__(self):
        self._token_id = None

    def set_token(self, token_id):
        self._token_id = token_id

    def read(self):
        return self._token_id


class _RFIDTokenBackend:
    """TODO: not built anywhere yet, on this console or on the device."""

    def read(self):
        raise NotImplementedError("RFID token backend not wired up yet")


class _MagneticTokenBackend:
    """TODO: not built anywhere yet, on this console or on the device."""

    def read(self):
        raise NotImplementedError("magnetic token backend not wired up yet")


BACKENDS = {
    "mock": _MockTokenBackend,
    "rfid": _RFIDTokenBackend,
    "magnetic": _MagneticTokenBackend,
}


class TokenReader:
    def __init__(self, backend="mock", roles=None):
        if backend not in BACKENDS:
            raise ValueError(f"unknown token backend: {backend!r}")
        self.backend_name = backend
        self._backend = BACKENDS[backend]()
        self._roles = roles or {}
        self._lock = threading.Lock()

    def set_mock_token(self, token_id):
        if not isinstance(self._backend, _MockTokenBackend):
            raise RuntimeError("set_mock_token requires the mock token backend")
        with self._lock:
            self._backend.set_token(token_id)

    def current_token(self):
        with self._lock:
            return self._backend.read()

    def role(self):
        token_id = self.current_token()
        if token_id is None:
            return "locked"
        return self._roles.get(token_id, "locked")
