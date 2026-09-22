"""Entry point: run the Voight-Kampff empathy test in a terminal.

Usage: PYTHONPATH=src python3 -m vk.cli
"""
from .config import load_config
from .engine import TestSession


def main():
    config = load_config()
    TestSession(config).run()


if __name__ == "__main__":
    main()
