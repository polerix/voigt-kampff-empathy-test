"""The operator/puppeteer web console, the subject-facing display kiosks,
and the JSON API that drives both.

This is deliberately one app, not two: run it with hardware_backend="mock"
in config (the default) and it's the "test the software" site with nothing
attached; point the same config at hardware_backend="real" on the actual
Pi and it's the "puppeteer the prop" site driving real GPIO/i2c/HDMI. There
is no reason to maintain two separate frontends for that.

Run with: python3 web/server.py
"""
import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vk.config import load_config  # noqa: E402
from vk.engine import TestSession  # noqa: E402
from vk.hardware.controller import HardwareController  # noqa: E402
from vk.hardware.service import PermissionDenied, ServicePanel  # noqa: E402
from vk.sensors import SensorHub  # noqa: E402

config = load_config(os.environ.get("VK_CONFIG"))
hardware = HardwareController(config)
sensors = SensorHub(poll_interval=config["sensor_poll_interval"])
session = TestSession(config, hardware, sensors)
service = ServicePanel(hardware, session.questions)
session.start()
hardware.displays.set_booted(True)

app = Flask(__name__)


def _state():
    snapshot = hardware.snapshot()
    snapshot["session"] = {
        "index": session.index,
        "running": session.running,
        "question_count": len(session.questions),
    }
    snapshot["backend"] = config["hardware_backend"]
    return snapshot


@app.route("/")
def index():
    return render_template("index.html", backend=config["hardware_backend"])


@app.route("/console")
def console():
    return render_template("console.html")


@app.route("/display/<int:screen>")
def display(screen):
    return render_template("display.html", screen=screen)


@app.route("/api/state")
def api_state():
    return jsonify(_state())


@app.route("/api/token", methods=["POST"])
def api_token():
    if hardware.tokens.backend_name != "mock":
        return jsonify({"error": "token backend is not mock; use the real reader"}), 403
    token_id = (request.get_json(force=True) or {}).get("token_id")
    hardware.tokens.set_mock_token(token_id or None)
    return jsonify(_state())


@app.route("/api/button/<name>", methods=["POST"])
def api_button(name):
    try:
        ok, reason = hardware.buttons.press(name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    status = 200 if ok else 409
    return jsonify({"ok": ok, "reason": reason, "state": _state()}), status


@app.route("/api/focus", methods=["POST"])
def api_focus():
    hardware.arm.focus_pulse()
    return jsonify({"ok": True})


@app.route("/api/deviation", methods=["POST"])
def api_deviation():
    value = (request.get_json(force=True) or {}).get("value", 0)
    session.set_deviation(float(value))
    if float(value) >= 75:
        hardware.sounds.play("deviation_alert")
    return jsonify(_state())


@app.route("/api/sensor-override", methods=["POST"])
def api_sensor_override():
    body = request.get_json(force=True) or {}
    field = body.get("field")
    if "value" not in body or body["value"] is None:
        sensors.clear_override(field)
    else:
        sensors.override(field, body["value"])
    return jsonify(_state())


@app.route("/api/jump", methods=["POST"])
def api_jump():
    body = request.get_json(force=True) or {}
    try:
        service._require_service_role()
    except PermissionDenied as exc:
        return jsonify({"error": str(exc)}), 403
    session.jump_to(int(body.get("index", 0)))
    return jsonify(_state())


@app.route("/api/service/gpio-check", methods=["POST"])
def api_service_gpio_check():
    try:
        return jsonify(service.check_gpio())
    except PermissionDenied as exc:
        return jsonify({"error": str(exc)}), 403
    except NotImplementedError as exc:
        return jsonify({"error": str(exc)}), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
