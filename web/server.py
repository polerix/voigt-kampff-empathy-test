"""The operator/puppeteer web console, the subject-facing display kiosks,
and the JSON API that drives both.

One app, not two: hardware_backend="mock" in config is the "test the
software" site (no broker needed); hardware_backend="real" is the
"puppeteer the prop" site, talking to the actual VK cluster's MQTT broker.
Same UI either way - see docs/design/mqtt-contract.md for the wire
protocol this thin client speaks.

Run with: python3 web/server.py
"""
import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vk.config import load_config  # noqa: E402
from vk.displays import DisplayState  # noqa: E402
from vk.engine import TestSession  # noqa: E402
from vk.hardware.controller import HardwareController  # noqa: E402
from vk.hardware.owl import SCREEN_CTL_PAYLOADS, SFX_BUTTON_ALIASES, SFX_EVENTS  # noqa: E402
from vk.hardware.service import PermissionDenied, ServicePanel  # noqa: E402
from vk.sensors import SensorHub  # noqa: E402

config = load_config(os.environ.get("VK_CONFIG"))
hardware = HardwareController(config)
sensors = SensorHub(poll_interval=config["sensor_poll_interval"])
display = DisplayState()
interview = TestSession(config, sensors, display)
service = ServicePanel(hardware, interview.questions)
interview.start_background()
display.set_booted(True)

app = Flask(__name__)


def _locked():
    return hardware.tokens.role() == "locked"


def _state():
    snapshot = hardware.snapshot()
    snapshot["display"] = display.snapshot()
    snapshot["interview"] = {
        "index": interview.index,
        "running": interview.running,
        "question_count": len(interview.questions),
    }
    return snapshot


@app.route("/")
def index():
    return render_template("index.html", backend=config["hardware_backend"])


@app.route("/console")
def console():
    return render_template(
        "console.html",
        sfx_events=SFX_EVENTS + SFX_BUTTON_ALIASES,
        screen_ctl_payloads=SCREEN_CTL_PAYLOADS,
    )


@app.route("/display/<int:screen>")
def display_page(screen):
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


def _guard():
    if _locked():
        return jsonify({"error": "no security token present"}), 403
    return None


@app.route("/api/arm", methods=["POST"])
def api_arm():
    if (guard := _guard()) is not None:
        return guard
    action = (request.get_json(force=True) or {}).get("action")
    try:
        hardware.arm.command(action)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_state())


@app.route("/api/arm/<joint>", methods=["POST"])
def api_arm_joint(joint):
    if (guard := _guard()) is not None:
        return guard
    action = (request.get_json(force=True) or {}).get("action")
    joints = {"shoulder": hardware.arm.shoulder, "elbow": hardware.arm.elbow, "wrist": hardware.arm.wrist}
    if joint not in joints:
        return jsonify({"error": f"unknown joint: {joint!r}"}), 404
    try:
        joints[joint](action)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_state())


@app.route("/api/bellows", methods=["POST"])
def api_bellows():
    if (guard := _guard()) is not None:
        return guard
    action = (request.get_json(force=True) or {}).get("action")
    if action == "on":
        hardware.bellows.on()
    elif action == "off":
        hardware.bellows.off()
    else:
        return jsonify({"error": f"unknown bellows action: {action!r}"}), 400
    return jsonify(_state())


@app.route("/api/worker", methods=["POST"])
def api_worker():
    if (guard := _guard()) is not None:
        return guard
    action = (request.get_json(force=True) or {}).get("action")
    if action == "start":
        hardware.worker.start()
    elif action == "stop":
        hardware.worker.stop()
    else:
        return jsonify({"error": f"unknown worker action: {action!r}"}), 400
    return jsonify(_state())


@app.route("/api/leds", methods=["POST"])
def api_leds():
    if (guard := _guard()) is not None:
        return guard
    body = request.get_json(force=True) or {}
    group, on = body.get("group"), body.get("on")
    groups = {"eye": hardware.leds.eye, "buttons": hardware.leds.buttons, "movie": hardware.leds.movie,
              "vus": hardware.leds.vus}
    if group == "buttons_boot":
        hardware.leds.buttons_boot()
    elif group in groups:
        groups[group](bool(on))
    else:
        return jsonify({"error": f"unknown led group: {group!r}"}), 400
    return jsonify(_state())


@app.route("/api/owl/display/<name>/<kind>", methods=["POST"])
def api_owl_display(name, kind):
    if (guard := _guard()) is not None:
        return guard
    displays = hardware.owl.displays()
    if name not in displays:
        return jsonify({"error": f"unknown display: {name!r}"}), 404
    value = (request.get_json(force=True) or {}).get("value", 0)
    try:
        if kind == "static":
            displays[name].set_static(value)
        elif kind == "roll":
            displays[name].set_roll(value)
        else:
            displays[name].set_fx(kind, value)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_state())


@app.route("/api/owl/fx-reset", methods=["POST"])
def api_owl_fx_reset():
    if (guard := _guard()) is not None:
        return guard
    hardware.owl.fx_reset()
    return jsonify(_state())


@app.route("/api/owl/sfx", methods=["POST"])
def api_owl_sfx():
    if (guard := _guard()) is not None:
        return guard
    event = (request.get_json(force=True) or {}).get("event")
    try:
        hardware.owl.sfx(event)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_state())


@app.route("/api/owl/screen-ctl", methods=["POST"])
def api_owl_screen_ctl():
    if (guard := _guard()) is not None:
        return guard
    payload = (request.get_json(force=True) or {}).get("payload")
    try:
        hardware.owl.screen_ctl(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_state())


@app.route("/api/interview/start", methods=["POST"])
def api_interview_start():
    if (guard := _guard()) is not None:
        return guard
    interview.start()
    return jsonify(_state())


@app.route("/api/interview/pause", methods=["POST"])
def api_interview_pause():
    if (guard := _guard()) is not None:
        return guard
    interview.pause()
    return jsonify(_state())


@app.route("/api/interview/deviation", methods=["POST"])
def api_interview_deviation():
    if (guard := _guard()) is not None:
        return guard
    value = (request.get_json(force=True) or {}).get("value", 0)
    interview.set_deviation(float(value))
    return jsonify(_state())


@app.route("/api/interview/sensor-override", methods=["POST"])
def api_interview_sensor_override():
    if (guard := _guard()) is not None:
        return guard
    body = request.get_json(force=True) or {}
    field = body.get("field")
    if "value" not in body or body["value"] is None:
        sensors.clear_override(field)
    else:
        sensors.override(field, body["value"])
    return jsonify(_state())


@app.route("/api/interview/jump", methods=["POST"])
def api_interview_jump():
    body = request.get_json(force=True) or {}
    try:
        service._require_service_role()
    except PermissionDenied as exc:
        return jsonify({"error": str(exc)}), 403
    interview.jump_to(int(body.get("index", 0)))
    return jsonify(_state())


@app.route("/api/service/check-bus", methods=["POST"])
def api_service_check_bus():
    try:
        return jsonify(service.check_bus())
    except PermissionDenied as exc:
        return jsonify({"error": str(exc)}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
