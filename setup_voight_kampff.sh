#!/bin/bash

# Script to install dependencies, set up SQLite database, and configure the Voight-Kampff machine
# Run this script on a Raspberry Pi with Raspberry Pi OS

# Update and install dependencies
echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-tk python3-pip python3-rpi.gpio python3-pygame sqlite3

# Install Python libraries
echo "Installing Python libraries..."
pip3 install kivy

# Create SQLite database and tables
echo "Setting up SQLite database and tables..."
DB_FILE="voight_kampff.db"
sqlite3 "$DB_FILE" <<EOF
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    name TEXT,
    badge_number TEXT
);
CREATE TABLE IF NOT EXISTS empathy_questions (
    id INTEGER PRIMARY KEY,
    question TEXT
);
EOF

# Make main.py executable
chmod +x main.py

echo "Setup complete! Run the Voight-Kampff machine using: ./main.py"
