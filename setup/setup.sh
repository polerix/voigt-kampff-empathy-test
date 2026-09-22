#!/bin/bash
# Bootstrap a Raspberry Pi (or any Linux box) to run the Voight-Kampff
# empathy test engine and its web viewer.
set -euo pipefail

echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

echo "Creating virtual environment..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python packages..."
pip install -r requirements.txt

echo "Setup complete."
echo "Run the terminal test:  PYTHONPATH=src .venv/bin/python -m vk.cli"
echo "Run the web viewer:     .venv/bin/python web/server.py"
