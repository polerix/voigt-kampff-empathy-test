# Visual & Sound Identity: ESPER / Spinner Cockpit

This project's terminal and dashboard aesthetic is deliberately drawn from
two other props in the *Blade Runner* universe, not just the Voight-Kampff
machine itself:

- **The ESPER photo-analysis terminal** (Deckard's apartment scene): a CRT
  readout driven by discrete voice/button commands, framed in a physical
  console with hard edges and analog dials.
- **The Spinner cockpit**: banks of amber and green backlit toggle switches,
  small monochrome CRT/vector readouts, and an ambient electrical hum
  underneath every interaction.

Both share a design language this project's web viewer borrows on purpose:

- Monospace, phosphor-green-on-black text (see `web/static/style.css`).
- Boxed, labeled instrument readouts rather than free-form text
  (`[CO2 000]  [O2 000]  [IRIS 000]  [PULSE 000]  [TIME 000]`), matching the
  interface mockups in `docs/interface-mockups/`.
- A deliberately mechanical, low-chrome UI: no gradients, no animation
  beyond what a real instrument panel would show.

## Sound (not yet implemented)

The props above are as much about sound as they are visual: switch clicks,
a low ambient hum, a distinct confirmation tone per input, a rising tone
during the biometric readout. This project does not yet implement any of
that — there is no audio pipeline, and no sound assets are checked in. If
sound is added later, it should follow the same restraint: discrete,
diegetic cues (startup chime, per-answer confirmation tone, an alert tone
on a "replicant" verdict) rather than a music bed.

## Adjacent prior art

An earlier sibling of this repository, `Tyrel_Voight-Campff_Empathy_Test`,
turned out on inspection to be an unrelated fork of
[alien-console](https://github.com/Swordfish90/cool-retro-term), a
terminal emulator for the MU/TH/UR computer from *Alien: Isolation* — a
different franchise, but the same retro-CRT-terminal design family. It has
been archived rather than merged in (its C/ncurses code has nothing to do
with this project's Python/Flask stack), but its CRT shader config
(`nostromo.json`) and startup-sound approach are worth noting as prior art
for the sound direction above, if it's ever picked up.
