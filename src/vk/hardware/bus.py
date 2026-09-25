"""The MQTT bus to the real VK prop cluster, plus a mock stand-in.

Real topology (see docs/design/mqtt-contract.md, mirrored from
BladeRunnerVK's own VK-MQTT-topic-contract.md): a mosquitto broker on
owl.local:1883, with Owl (master) and Tyrell (worker) as the two nodes that
matter to this console. This client never runs GPIO itself - it only
publishes/subscribes, exactly like the existing terminal Message Control
Console does.

Two facts are tracked separately and never merged, per the contract's own
design: whether *this console* has a broker connection (bus_up), and
whether *Tyrell* is alive behind it (tyrell_status: online/offline/unknown).
A publish to a powered-off Tyrell succeeds at the broker - without the
second fact that would be indistinguishable from success.
"""
import threading

import paho.mqtt.client as mqtt

_SUBSCRIBE_TOPICS = ("vk/from/tyrell/reply", "vk/from/tyrell/status", "vk/state", "vk/glitch")


class VKBus:
    def __init__(self, host="owl.local", port=1883, client_id="vk-web-console", reply_timeout=1.5):
        self.reply_timeout = reply_timeout
        self._client = mqtt.Client(client_id=client_id)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._lock = threading.Lock()
        self._bus_up = False
        self._tyrell_status = "unknown"  # online | offline | unknown
        self._vk_state = None
        self._glitch = False
        self._last_reply = None
        self._host = host
        self._port = port

    def connect(self):
        self._client.connect_async(self._host, self._port)
        self._client.loop_start()

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        with self._lock:
            self._bus_up = reason_code == 0 or reason_code == "Success"
        if self._bus_up:
            for topic in _SUBSCRIBE_TOPICS:
                client.subscribe(topic)

    def _on_disconnect(self, client, userdata, reason_code, properties=None):
        with self._lock:
            self._bus_up = False
            self._tyrell_status = "unknown"

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode(errors="replace").strip()
        with self._lock:
            if msg.topic == "vk/from/tyrell/status":
                self._tyrell_status = payload
            elif msg.topic == "vk/from/tyrell/reply":
                self._last_reply = payload
            elif msg.topic == "vk/state":
                self._vk_state = payload
            elif msg.topic == "vk/glitch":
                self._glitch = True

    def publish(self, topic, payload):
        self._client.publish(topic, str(payload))

    def clear_glitch(self):
        with self._lock:
            self._glitch = False

    def snapshot(self):
        with self._lock:
            return {
                "backend": "real",
                "bus_up": self._bus_up,
                "tyrell_status": self._tyrell_status,
                "vk_state": self._vk_state,
                "glitch": self._glitch,
                "last_reply": self._last_reply,
            }


class MockBus:
    """Stands in for VKBus with no broker attached. Publishes are just
    logged, not sent anywhere - this is what backs the "test the software"
    site. tyrell_status stays "online" so the console UI behaves as if a
    healthy Tyrell were listening.
    """

    def __init__(self, *_, **__):
        self._lock = threading.Lock()
        self.log = []
        self._vk_state = "MAIN"
        self._glitch = False

    def connect(self):
        pass

    def disconnect(self):
        pass

    def publish(self, topic, payload):
        with self._lock:
            self.log.append((topic, str(payload)))

    def clear_glitch(self):
        with self._lock:
            self._glitch = False

    def snapshot(self):
        with self._lock:
            return {
                "backend": "mock",
                "bus_up": True,
                "tyrell_status": "online",
                "vk_state": self._vk_state,
                "glitch": self._glitch,
                "last_reply": self.log[-1][1] if self.log else None,
            }
