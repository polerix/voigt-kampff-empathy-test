# Voight-Kampff Empathy Test

A software emulation of the Voight-Kampff empathy test prop from *Blade
Runner* and, to some extent, the novel *Do Androids Dream of Electric
Sheep?* — a web console for the physical prop, a 3D simulation view, plus
the interview application (fixed question script, fake physiological
readout, results log) that runs alongside it.

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

## Architecture

The physical prop is a separate, more mature project — Trevor Gertridge's
`BladeRunnerVK`, a cluster of Raspberry Pis (Owl master, Tyrell worker)
talking over MQTT. This repo doesn't reimplement that; it's a thin client
against it, plus its own interview application and a 3D simulation view
layered on top. See [docs/design/device.md](docs/design/device.md) and
[docs/design/mqtt-contract.md](docs/design/mqtt-contract.md) for the full
picture.

```
src/vk/
  hardware/
    bus.py         MQTT client (VKBus) + MockBus for the no-broker test site
    actuators.py    Tyrell: arm (shoulder/elbow/wrist), bellows, worker
                    macro, LEDs, A/V stub - tracks last-commanded
                    (optimistic, not confirmed) state for the 3D sim
    owl.py          Owl: OLED/HDMI static/roll/FX, sfx, screen_ctl
    tokens.py       console-side security gate (not device-enforced)
    controller.py   composes the above from config
    service.py      service-mode: bus diagnostics, question-script overrides
  questions.py, data/questions.csv   the fixed interview script
  sensors.py         fake physiological data generator
  results.py         per-question CSV log
  engine.py           ties the script to an explicit start/pause control
web/
  server.py           Flask app: console, 3D sim, display kiosks, JSON API
  templates/          index.html, console.html, simulation.html, display.html
  static/vendor/three/  vendored three.js (MIT) - no CDN dependency
  static/models/         real prop mesh goes here once available (not yet)
```

One app, one switch: `hardware_backend: "mock"` in config runs the whole
stack with no broker attached (the "test the software" site);
`hardware_backend: "real"` talks to the actual VK prop's MQTT broker (the
"puppeteer the prop" site). Same console UI either way.

## Running it

```
pip install -r requirements.txt
python3 web/server.py
```

Defaults to `hardware_backend: "mock"` — no broker needed. Open `/` for
status, `/console` to puppeteer it, `/simulation` for the 3D view,
`/display/1` (2, 3) for the subject-facing interview readout screens.

To talk to the real prop: write a JSON config with `"hardware_backend":
"real"` and the right `mqtt_host`/`mqtt_port` (defaults to
`owl.local:1883`), then run with `VK_CONFIG=path/to/config.json python3
web/server.py`.

On a fresh Raspberry Pi, `setup/setup.sh` installs Python, creates a
virtualenv, and installs dependencies.

## What's deliberately not real, or not yet wired up

- Fake sensor data (permanent, by design) and per-question
  `expected_response` text (calibration data that belongs to the physical
  test — `src/vk/data/questions.csv` ships with it blank).
- A/V recording — a local subprocess on Tyrell's Pi, outside the MQTT bus
  entirely. Not controllable from this console.
- The token drawer — not integrated into the physical prop at all yet.
  This console's token gate is a software-only safety check.
- Whether the interview readout should eventually route onto Owl's real
  OLED/HDMI displays instead of this app's own `/display/<n>` pages.
- The 3D simulation is placeholder geometry with optimistic (not
  telemetry-confirmed) joint animation — see
  [docs/design/device.md](docs/design/device.md#3d-simulation-simulation)
  for the real GoldenArmor mesh swap-in point and why it isn't in yet
  (format/poly-count/licensing, all unresolved).

## Related repos

This project used to be split across three repos, since folded into this
one and archived:

- `voight-kampff-model` held 3D-printable hardware files (servo/bellows
  parts). Hardware design files, out of scope for this repo, kept locally.
- `Tyrel_Voight-Campff_Empathy_Test` turned out to be an unrelated fork of
  a different project (an *Alien: Isolation* terminal emulator) — wrong
  franchise, C instead of Python. Nothing from it was carried over.

The physical prop's actual driver code lives in Trevor Gertridge's
[BladeRunnerVK](https://github.com/TrevorGertridge/BladeRunnerVK) — this
repo talks to it over MQTT rather than vendoring or forking it. The
intended 3D-simulation mesh is GoldenArmor's Voight-Kampff model — not yet
integrated, see above.
