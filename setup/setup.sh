#!/bin/bash
# Bootstrap a Raspberry Pi (or any Linux box) to run the Voight-Kampff
# empathy test engine and its web console.
set -euo pipefail

echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip alsa-utils

echo "Creating virtual environment..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python packages..."
pip install -r requirements.txt

echo "Generating placeholder sound cues (replace with real audio later)..."
.venv/bin/python setup/generate_placeholder_sounds.py

echo "Setup complete."
echo "Run the web console (defaults to hardware_backend=mock):"
echo "  .venv/bin/python web/server.py"
echo "To drive the real prop, set hardware_backend to \"real\" in a config"
echo "file and point VK_CONFIG at it before running."
