#!/usr/bin/env python3
"""Synthesizes short placeholder beep tones for each sound event so the
trigger wiring (button presses, deviation alert, stimulus tone) is
testable before real recordings exist. These are plain sine-wave beeps,
not attempts at a final sound design - replace the files in sounds/ with
real audio whenever it's ready.

Usage: python3 setup/generate_placeholder_sounds.py
"""
import math
import os
import struct
import wave

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "..", "sounds")
SAMPLE_RATE = 44100

# (event name, frequency Hz, duration seconds)
TONES = [
    ("button_activate", 880.0, 0.12),
    ("button_suspend", 440.0, 0.12),
    ("deviation_alert", 220.0, 0.6),
    ("stimulus_tone", 660.0, 0.25),
]


def write_tone(path, frequency, duration):
    n_samples = int(SAMPLE_RATE * duration)
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            # fade in/out over 10ms to avoid clicks
            fade = min(1.0, i / (SAMPLE_RATE * 0.01), (n_samples - i) / (SAMPLE_RATE * 0.01))
            sample = int(32767 * 0.4 * fade * math.sin(2 * math.pi * frequency * t))
            frames += struct.pack("<h", sample)
        wav_file.writeframes(bytes(frames))


def main():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    for name, freq, duration in TONES:
        path = os.path.join(SOUNDS_DIR, f"{name}.wav")
        write_tone(path, freq, duration)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
