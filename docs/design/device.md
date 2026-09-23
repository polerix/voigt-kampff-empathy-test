# Device reference

What the physical prop actually does, as the software models it. Replaces
the earlier CRT/ESPER-Spinner aesthetic notes — the brief now is accuracy
and functionality, not a visual theme, so this document is the real I/O
reference instead.

## Token drawer / security

A manual latch spring opens the drawer (no motor). An RFID or magnetic
token is placed inside, the drawer is closed. There is no username or
password — the currently-present token's role is the entire auth model:

- No token → `locked`. Button LEDs stay off; nothing can run.
- Operator token → `operator`. Normal test mode.
- Service token → `service`. GPIO check, motion/timing calibration —
  a different token from the operator one.

See `src/vk/hardware/tokens.py`. The real reader (RFID vs magnetic) isn't
picked yet — both are stubbed pending the actual hardware.

## The three buttons

Square white buttons, pressed in order: camera arm → pheromone bellows
(fan) → A/V recording. Each toggles its mechanism between active and
suspended; its LED only lights with a token present. Activation and
suspension each have their own sound cue. The current code enforces the
order as a hard interlock (a button won't arm until the ones before it are
active) — flagged as an assumption in `hardware/buttons.py`, since the spec
describes "sequentially" without saying explicitly whether it's enforced.

The camera on the arm has its own manual focus button, separate from the
three panel buttons and not gated by the token.

## Screens

Three subject-facing displays. They never show question text — the agent
reads the fixed script aloud from a paper copy — and take no input. On
boot they show a status/accreditation sequence (real copy TODO — see
`web/templates/display.html`). During a test they show the fake
physiological readout and the operator-set expected-response reference and
deviation level.

## Fake physiological data

There's no real CO2, O2, pupillary, or reaction-time sensor — this is a
prop, and fake data is used on purpose, not as a placeholder for something
real later (`src/vk/sensors.py`). Values free-run as a random walk; any
field can be pinned from the console for a specific run.

## Question script and the A/V button

The questions are always the same, fixed order, no randomization
(`src/vk/data/questions.csv`). The A/V button starts and pauses the
question timer: each question counts down on its own time limit while A/V
is active, auto-advancing at zero; pausing freezes the countdown. A
stimulus tone plays at each question boundary.

`expected_response` per question is calibration data that belongs to the
physical test — the CSV ships with it blank (`TODO`) rather than invented.

## Sounds

Four events: button activation, button suspension, a deviation alert, and
the per-question stimulus tone. No audio assets are checked in — see
`sounds/README.md` for the expected filenames and a script that generates
placeholder tones so the trigger wiring is testable before real recordings
exist.

## The web console

One Flask app (`web/server.py`), not three separate sites:

- `hardware_backend: "mock"` in config → the "test the software" site:
  same UI, no prop attached.
- `hardware_backend: "real"` → the "puppeteer the prop" site: same UI,
  now driving actual GPIO/i2c/HDMI.

`/console` is the puppeteer control surface (buttons, focus, deviation,
sensor overrides, service-mode panel). `/display/<n>` is what each of the
three subject-facing screens shows. `/api/state` is the JSON both poll.

## What's still a stub

Real GPIO pin numbers (`config.gpio_pins`), the RFID/magnetic reader
choice, the arm motor / bellows relay / A/V capture pipeline, and GPIO
diagnostics/motion calibration in service mode are all documented
`NotImplementedError` stubs — there's no hardware here to wire them up
against. Fill in `config.gpio_pins` and swap `hardware_backend` to `"real"`
once the actual wiring is known.
