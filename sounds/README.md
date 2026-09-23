# Sound cues

Four events, each expecting a `<name>.wav` file in this directory when
`hardware_backend` is `"real"` (the mock backend never touches these files):

- `button_activate.wav` — a button was pressed on (arm raised, bellows
  started, A/V started)
- `button_suspend.wav` — a button was pressed off
- `deviation_alert.wav` — deviation crossed the alert threshold
- `stimulus_tone.wav` — played at each question boundary (a timed stimulus,
  like the questions themselves)

No audio files are checked into this repo. Run
`python3 setup/generate_placeholder_sounds.py` to generate short sine-wave
placeholder tones for all four, so the trigger wiring can be tested before
real recordings exist. Replace them with real audio whenever it's ready —
same filenames, any format `aplay` can play.
