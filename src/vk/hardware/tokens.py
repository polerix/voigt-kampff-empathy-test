"""Security token detection for the token drawer.

The drawer opens on a manual latch spring (no motor involved); a token
(RFID tag or magnetic card, backend-dependent) is placed inside and the
drawer is closed. There is no username or password - the currently-detected
token's role (from config) is the entire auth model:

  no token         -> "locked"   (button LEDs stay off, no test can run)
  operator token   -> "operator" (normal test mode)
  service token    -> "service"  (GPIO check, motion/timing calibration)
"""
import threading


class _MockTokenBackend:
    """Software-only: the token id is set programmatically (from the
    puppeteer console), standing in for a reader with no hardware attached."""

    def __init__(self):
        self._token_id = None

    def set_token(self, token_id):
        self._token_id = token_id

    def read(self):
        return self._token_id


class _RFIDTokenBackend:
    """TODO: real backend for an I2C/SPI RFID reader (e.g. MFRC522).

    Not implemented - no reader hardware available to test against here.
    """

    def read(self):
        raise NotImplementedError("RFID token backend not wired up yet")


class _MagneticTokenBackend:
    """TODO: real backend for a magnetic-stripe or reed/hall sensor reader.

    Not implemented - no reader hardware available to test against here.
    """

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
        """Only valid with the mock backend; used by the test-software site."""
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
