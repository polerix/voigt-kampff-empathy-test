"""Flask app: public showcase page + live operator dashboard.

Run with: python3 web/server.py
"""
import os
import sys

from flask import Flask, jsonify, render_template, send_from_directory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vk.state import SharedState  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")

app = Flask(__name__)


@app.route("/")
def showcase():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/state")
def api_state():
    return jsonify(SharedState.instance().snapshot())


@app.route("/brand/<path:filename>")
def brand_assets(filename):
    """Serves the repo-root branding images (Pavlov Institute logo, PI ASCII art)."""
    return send_from_directory(REPO_ROOT, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
