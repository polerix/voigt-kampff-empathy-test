"""Terminal rendering for the Voight-Kampff interview interface."""
import os


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


class TerminalUI:
    def show_header(self, reading):
        _clear()
        print("+========================================================+")
        print("|            VOIGHT-KAMPFF MACHINE                       |")
        print("|                 NEXUS-6 EDITION                        |")
        print("+========================================================+")
        print(
            f"[CO2 {reading.co2}]  [O2 {reading.o2}]  [IRIS {reading.iris}]  "
            f"[PULSE {reading.pulse}]  [TIME {reading.elapsed:.0f}]\n"
        )

    def show_question(self, question, reading, time_left):
        self.show_header(reading)
        print("  " + question.text + "\n")
        if question.time_limit:
            filled = int((1 - time_left / question.time_limit) * 50)
        else:
            filled = 50
        filled = max(0, min(50, filled))
        print(" " * filled + "#" * (50 - filled))
        print("\n  [back]  [next]")

    def show_results(self, reading):
        _clear()
        print("  +============================+")
        print("  |  SENSOR READINGS           |")
        print("  +============================+")
        print("  |  CO2:  {:<18}|".format(reading.co2))
        print("  |  O2:   {:<18}|".format(reading.o2))
        print("  |  IRIS: {:<18}|".format(reading.iris))
        print("  +============================+\n")

    def show_error(self, msg):
        _clear()
        print(f"  Error: {msg}\n")
