#!/bin/bash
# Bootstrap a Raspberry Pi (or any Linux box) to run the Voight-Kampff
# web console.
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
echo "Run the web console (defaults to hardware_backend=mock, no broker needed):"
echo "  .venv/bin/python web/server.py"
echo "To talk to the real VK prop bus, write a JSON config with"
echo "  \"hardware_backend\": \"real\" and the right mqtt_host, then run:"
echo "  VK_CONFIG=path/to/config.json .venv/bin/python web/server.py"
