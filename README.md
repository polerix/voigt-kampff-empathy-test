# Voight-Kampff Empathy Test

A software emulation of the Voight-Kampff empathy test prop from *Blade
Runner* and, to some extent, the novel *Do Androids Dream of Electric
Sheep?* — a token-gated control panel, a fixed question script timed off
an A/V button, and subject-facing readout screens, meant to run on a
Raspberry Pi.

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

## How the physical device works

- A token drawer (manual latch spring, no motor) is the entire auth model —
  no username or password. No token present means the three button LEDs
  stay off and nothing can run. A separate service token unlocks GPIO
  checks and motion/timing calibration instead of normal test mode.
- Three square white buttons — camera arm, pheromone bellows (fan), A/V
  recording — pressed in that order. Each toggles active/suspended, lights
  its own LED once a token is present, and plays an activation or
  suspension sound. The camera on the arm has its own manual focus button.
- The A/V button starts and pauses the question script's timer. The
  questions are always the same, fixed order — no randomization, and no
  question text is ever shown on screen. A human agent reads each question
  aloud from a paper copy of the same script.
- Three subject-facing screens boot through a status/accreditation
  sequence, then show the fake physiological readout plus an
  operator-puppeteered expected-response reference and deviation level.
  They take no input.
- There's no real CO2/O2/pupil-dilation/reaction-time sensor — this is a
  prop, so fake data is used, on purpose, permanently (not a placeholder
  for real sensors later).
- A web console, served over wifi from the Pi, has every control needed to
  puppeteer the prop: buttons, focus, deviation, and fake-sensor overrides.

Full reference: [docs/design/device.md](docs/design/device.md).

## Architecture

One Flask app, not three separate sites, with a single backend switch:

- `hardware_backend: "mock"` in config → run the whole stack with no prop
  attached, for developing/testing the software itself.
- `hardware_backend: "real"` → the same app drives actual GPIO/i2c/HDMI on
  the Pi to puppeteer the physical prop.

```
src/vk/
  hardware/    tokens, buttons, actuators (arm/bellows/A-V), sounds,
               displays, service-mode panel — mock and real backends
  questions.py the fixed question script (data/questions.csv)
  sensors.py   fake physiological data generator
  results.py   per-question CSV log (expected response, deviation, sensors)
  engine.py    ties the script to the A/V button's timer
web/
  server.py      Flask app: console, display kiosks, JSON API
  templates/     index.html (status), console.html (operator/puppeteer),
                 display.html (subject-facing kiosk, parameterized by screen #)
docs/design/device.md        full device reference
docs/interface-mockups/      boot-screen ASCII mockup
sounds/                      placeholder tone generator + expected filenames
setup/setup.sh               Raspberry Pi bootstrap script
```

## Running it

```
pip install -r requirements.txt
python3 setup/generate_placeholder_sounds.py   # optional: placeholder audio
python3 web/server.py
```

Defaults to `hardware_backend: "mock"` — no prop needed. Open `/` for
status, `/console` to puppeteer it, `/display/1` (2, 3) for the
subject-facing screens.

To drive the real prop: write a JSON config with `"hardware_backend":
"real"`, real `token_backend` (`"rfid"` or `"magnetic"`), `token_roles`,
and `gpio_pins`, then run with `VK_CONFIG=path/to/config.json python3
web/server.py`. The real actuator/token/sound backends are documented
stubs (`NotImplementedError`) until that wiring is filled in — see
`docs/design/device.md#whats-still-a-stub`.

On a fresh Raspberry Pi, `setup/setup.sh` installs Python, ALSA, creates a
virtualenv, and installs dependencies.

## What's deliberately not real

Fake sensor data (permanent, by design) and per-question
`expected_response` text (calibration data that belongs to the physical
test — `src/vk/data/questions.csv` ships with it blank). Not yet real:
GPIO pin wiring, the RFID/magnetic token reader, the arm motor / bellows
relay / A/V capture pipeline, and service-mode GPIO diagnostics /
calibration.

## Related repos

This project used to be split across three repos. They have been folded
into this one and archived:

- `voight-kampff-model` held 3D-printable hardware files (servo/bellows
  parts) for the physical build. Those are hardware design files, out of
  scope for this repo's software-and-web focus, and are kept locally
  rather than in git.
- `Tyrel_Voight-Campff_Empathy_Test` turned out, on inspection, to be an
  unrelated fork of a different project entirely (a terminal emulator for
  *Alien: Isolation*'s MU/TH/UR computer) — wrong franchise, C instead of
  Python. None of its code was carried over.
