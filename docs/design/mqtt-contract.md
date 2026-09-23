# VK Prop — MQTT Topic Contract

Mirrored from Trevor Gertridge's `BladeRunnerVK` repo
(`VK-MQTT-topic-contract.md`, verified against Owl v101 / Tyrell v0027).
This is the wire protocol `src/vk/hardware/` speaks — copied here so this
repo's own hardware layer can be checked against it without needing
BladeRunnerVK cloned locally. If the two ever disagree, BladeRunnerVK is
the source of truth; update this copy, not the other way around.

Broker: mosquitto on `owl.local:1883`.

## Direction is encoded in the prefix

| Prefix | Direction | Who subscribes |
|---|---|---|
| `vk/tyrell/…` | → Tyrell | Tyrell, via `vk/tyrell/#` |
| `vk/owl/…` | → Owl | Owl, 16 explicit topics |
| `vk/from/tyrell/…` | Tyrell → | Owl (and this console) |
| `vk/state`, `vk/glitch` | Owl → | Node-RED, this console |

`vk/tyrell/#` is strictly inbound — anything published beneath it,
including a reply, comes straight back to Tyrell as a command. That is why
the return path lives on `vk/from/tyrell/…` and not `vk/tyrell/reply`.

## Owl → Tyrell (commands)

| Topic | Payloads |
|---|---|
| `vk/tyrell/arm` | `raise` `lower` `home` `abort` `boothome-on` `boothome-off` `sethome` `forget` `state` |
| `vk/tyrell/elbow` | `extend` `retract` `stop` |
| `vk/tyrell/shoulder` | `extend` `retract` |
| `vk/tyrell/wrist` | `extend` `retract` |
| `vk/tyrell/bellows` | `on` `off` |
| `vk/tyrell/leds` | `eye_on` `eye_off` `buttons_on` `buttons_off` `buttons_boot` `movie_on` `movie_off` `vus_on` `vus_off` |
| `vk/tyrell/worker` | `start` `stop` (macro; expands into arm + bellows commands) |

## Tyrell → Owl (return path)

| Topic | Retained | Payload |
|---|---|---|
| `vk/from/tyrell/reply` | no | one line of command output |
| `vk/from/tyrell/status` | yes | `online` \| `offline` (Last Will and Testament) |

## → Owl (commands)

CRT levels (integer 0–100, clamped): `vk/owl/displayA/static`,
`.../roll`, `vk/owl/displayB/static`, `.../roll`, `vk/owl/displayM/static`,
`.../roll`.

FX knobs (integer 0–100): `vk/owl/displayA/fx/teeth` `…/spike` `…/tilt`
`…/pulse`; `vk/owl/displayB/fx/shape` `…/tuck` `…/pulse`; `vk/owl/fx/reset`
(all knobs to default, payload ignored). No FX knobs on displayM.

`vk/owl/sfx`: `button` `function` `iris` `screen` `bellows_on`
`bellows_off` `static_on` `static_off` (`button1`/`button2`/`button3`
accepted as aliases of `button`).

`vk/owl/screen_ctl` (24 payloads): `all_black` `all_static` — `a_home`
`a_next` `a_prev` — `b_home` `b_next` `b_prev` — `main_home` `main_next`
`main_prev` `main_vkos` — `vkos_next` `vkos_prev` `vkos_auto_on`
`vkos_auto_off` — `main_quiz_start` `main_quiz_next` `main_quiz_prev`
`main_quiz_scroll_up` `main_quiz_scroll_down` — `main_video_start`
`main_video_next` `main_video_prev`.

## Owl → (outbound)

| Topic | Payload | When |
|---|---|---|
| `vk/state` | `BOOT` `MAIN` `SHELL` `INQUIRY` `DEBUG` `VIDEO` `OFF` `STATIC` `CALIBRATION` `VKOS` | on mode change |
| `vk/glitch` | `TRUE` | on leaving video playback |

Owl has no reply topic — its command confirmations are pushed straight
into its own local Message Control Console pane, not back over the bus.

## Not on the bus

- **A/V recording** — a local camera/mic subprocess Tyrell shells out to
  directly. Not addressable over MQTT; `AVRecorder`'s real backend is a
  documented stub until/unless that changes.
- **Token drawer / security** — not integrated into Tyrell or Owl at all
  yet. This console's token gate (`hardware/tokens.py`) is a software-only
  safety seatbelt with nothing on the device side enforcing it.

## Two facts, not one

Owl (and this console) track these separately and never merge them:
**bus up/down** (do we have a broker connection) and **Tyrell
online/offline/unknown** (is Tyrell alive behind it). A publish to a
powered-off Tyrell succeeds at the broker — without the second fact that's
indistinguishable from success.
