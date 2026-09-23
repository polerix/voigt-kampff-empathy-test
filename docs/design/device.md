# Device reference

What this repo's web console actually controls, and how it's wired to the
real prop.

## Two separate hardware efforts

This repo's software (the empathy-test question script, fake
physiological readout, results log) is one concern. The physical prop
itself — arm, bellows, LEDs, displays, sound — is a separate, more mature
codebase: Trevor Gertridge's `BladeRunnerVK`, a distributed cluster of
Raspberry Pis talking over MQTT (mosquitto on `owl.local:1883`). This
repo's `src/vk/hardware/` is a thin client against that bus, not a
reimplementation of it — see
[docs/design/mqtt-contract.md](mqtt-contract.md) for the exact wire
protocol, mirrored from `VK-MQTT-topic-contract.md` in that repo.

## Tyrell (worker): the physical prop

- **Arm** is three independently-commanded joints — shoulder, elbow,
  wrist — plus a macro-level `arm` topic (raise/lower/home/abort/etc.).
  There's no single "raised" boolean; Tyrell tracks its own homing state.
- **Bellows** is a single on/off servo.
- **LEDs**: four independent groups — eye, buttons (plus a boot pattern),
  movie, VU meters. Not one LED per panel button.
- **`worker start`/`stop`** is a macro that expands into arm + bellows
  commands — the closest real equivalent to "run the whole physical
  performance."
- **A/V recording is not on the bus.** Tyrell shells out to a local
  camera/mic subprocess directly. This console can't observe or drive it;
  `AVRecorder`'s real backend stays a stub until that changes.
- **The token drawer isn't integrated on the device at all yet.** This
  console's token gate is a software-only safety seatbelt — it stops the
  console UI from sending real commands without being "unlocked" first,
  but Tyrell and Owl don't check it themselves.

## Owl (master): displays and sound

Two OLEDs (`displayA`, `displayB`) plus one HDMI (`displayM`), each with
CRT static/roll levels; A and B additionally have glitch-FX knobs (teeth/
spike/tilt/pulse on A, shape/tuck/pulse on B) — this is a real glitch/iris
FX engine, not literal boot text. A 10-mode screen state machine
(`BOOT/MAIN/SHELL/INQUIRY/DEBUG/VIDEO/OFF/STATIC/CALIBRATION/VKOS`)
broadcasts on `vk/state`. Owl also owns the prop's actual sound output
(`sfx`: button/function/iris/screen/bellows_on/bellows_off/static_on/
static_off) — there is no separate local sound system in this repo
anymore; a previous version's `hardware/sounds.py` played placeholder
tones locally and has been retired now that Owl's real `sfx` vocabulary is
known.

Owl has no reply topic; this console tracks "last commanded" values for
display/FX/sfx, not confirmed state, except for `vk/state` and
`vk/glitch`, which Owl does broadcast.

## This repo's own layer, on top

The question script (`src/vk/questions.py`, `data/questions.csv`), fake
physiological readout (`src/vk/sensors.py`), and results log
(`src/vk/results.py`) are independent of the Tyrell/Owl bus — they model
the empathy-test *interview*, not the prop hardware. The `/display/<n>`
kiosk pages currently show this application's own simulated readout, not
Owl's real OLED/HDMI content. Whether/how those should eventually be the
same thing — e.g. routing the interview readout onto Owl's real displays
via `main_quiz_*` screen_ctl payloads — is still open; nothing currently
assumes they're connected.

The question-script timer used to be tied to an "A/V button." Since A/V
turned out to be off-bus, the timer now has its own explicit start/pause
control in the console, decoupled from any physical button.

## What's still open

- Whether/how the interview layer's readout should route onto Owl's real
  displays.
- Token drawer integration, if/when it gets built on the device side.
- A/V recording, if it's ever exposed over the bus instead of being a
  local subprocess.
