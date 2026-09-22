# Voight-Kampff Empathy Test

A software emulation of the Voight-Kampff empathy test from the movie
*Blade Runner* and, to some extent, the novel *Do Androids Dream of Electric
Sheep?*

It is an interpretation of the terminal interface used to present questions,
correlate sensor data, and generate a fictional diagnostic to determine
whether the subject is a REPLICANT or HUMAN.

The Voight-Kampff Empathy Test was designed to distinguish androids from
humans by measuring their capacity for empathy. The test had limitations —
some humans with mental illnesses, such as schizophrenia, might fail it.

## Historical background (in-universe)

The original Voigt Empathy Test was developed by the Pavlov Institute in
the Soviet Union after some T-14 androids managed to remain undetected for
up to a year. Around 1989/2018, Lurie Kampff modified the Voigt scale,
creating the Voight-Kampff Altered Scale, which became the standard method
of testing.

Bounty hunters themselves were required to pass the test before using it on
suspected androids. In early 1992/2021, bounty hunter Dave Holden
administered the test to three Nexus-6 androids. During the third test,
android Max Polokov shot Holden and escaped. Rick Deckard then took over
Holden's assignment, conducting tests on Rachael Rosen, Luba Luft, and Phil
Resch.

The Voight-Kampff test first appeared in *Do Androids Dream of Electric
Sheep?* and was later featured in its film adaptation, *Blade Runner*.
While the spelling was altered in the movie, the original spelling was
retained in the 1997 video game and the continuation novels by K. W. Jeter.

## Disclaimer

No ownership of the Voight-Kampff name, *Blade Runner*, or any associated
intellectual property is claimed. This project is a personal work created
for self-education and non-commercial purposes.

## Project status

This repository is the single home for the project: a Python test engine
meant to run on a Raspberry Pi, plus a web viewer (a public showcase page
and a live operator dashboard). It was consolidated from three previously
separate, overlapping repos — see [Related repos](#related-repos) below.

Currently implemented:

- A terminal-driven interview engine (`src/vk/`) that walks a question bank,
  times each answer, and records responses to a CSV results log.
- Mock sensor readings (CO2, O2, iris color, pulse) on a background thread,
  standing in for the real hardware sensors the final Raspberry Pi build
  will use — see `src/vk/sensors.py` for where a real hardware backend
  would plug in.
- A Flask web viewer (`web/`) with a static showcase page and a live
  operator dashboard that polls the same sensor/session state the terminal
  engine is using.

Not yet implemented: real hardware sensor backends (CO2/O2/altitude
sensors, an eye-tracking webcam), and any sound design — see
[docs/design/aesthetic.md](docs/design/aesthetic.md) for the documented,
not-yet-built direction on both.

## Running it

Terminal test engine:

```
pip install -r requirements.txt   # only needed for the web viewer
PYTHONPATH=src python3 -m vk.cli
```

Web viewer (showcase page at `/`, live dashboard at `/dashboard`):

```
pip install -r requirements.txt
python3 web/server.py
```

On a fresh Raspberry Pi, `setup/setup.sh` installs Python, creates a
virtualenv, and installs dependencies.

## Layout

```
src/vk/                  terminal test engine (questions, sensors, results, UI)
web/                      Flask app: showcase page + live operator dashboard
docs/design/              visual & sound identity notes
docs/interface-mockups/   ASCII mockups the terminal UI is based on
setup/setup.sh            Raspberry Pi bootstrap script
```

## Related repos

This project used to be split across three repos. They have been folded
into this one and archived:

- `voight-kampff-model` held 3D-printable hardware files (servo/bellows
  parts) for a physical VK-machine build. Those are hardware design files,
  out of scope for this repo's software-and-web focus, and are kept
  locally rather than in git.
- `Tyrel_Voight-Campff_Empathy_Test` turned out, on inspection, to be an
  unrelated fork of a different project entirely (a terminal emulator for
  *Alien: Isolation*'s MU/TH/UR computer) — wrong franchise, C instead of
  Python. It's referenced in [docs/design/aesthetic.md](docs/design/aesthetic.md)
  as adjacent prior art for the retro-CRT-terminal look, but none of its
  code was carried over.
