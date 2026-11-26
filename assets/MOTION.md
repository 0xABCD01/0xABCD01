# Motion system — inferno set (v4)

Theme chain: v1 lucu-seram (Halloween) → v3 "seram, bukan seram horror"
(eerie watcher) → v4, in the user's words: **seram dark laki banget,
berapi-api, dan unik**. Seriously dark, very masculine, on fire, unique.
Still no horror: no ghosts, no gore, no jumpscare. Fire and darkness.

The watcher from v3 stays, rebuilt broader — wide shoulder bar, angled
torso, thick strokes, wide stance — and his eyes now burn orange (ember
shell, pale core) instead of glowing red. Fire runs through every scene:
a fire line under the banner, a brazier, lava cracks in the hill, a
burning rooftop, rising embers everywhere, a howling wolf, and a shadow
whose own eyes burn back at you.

Built with the motion skills in `~/workspace/custom-skills/`
(`motion-design`, `motion-foundations`, `motion-patterns`,
`motion-advanced`). Generator: `generate_inferno.py`.

## Personality: TENSE + FIERCE

The watcher keeps the slow v3 timing (stillness is the threat). Fire is
the fast layer: flame flicker is irregular — three uneven keyframe stops
at ~1 s, per-flame duration and negative delay so no two flames sync —
and embers rise at crawl speed, drifting sideways as they fade.

## Tokens

| Token | Value | Used for |
|---|---|---|
| smooth | `cubic-bezier(0.22, 1, 0.36, 1)` | walks across frame |
| sine | `cubic-bezier(0.37, 0, 0.63, 1)` | living loops, smoke at 2x |
| sharp | `cubic-bezier(0.4, 0, 0.2, 1)` | glitch cuts, eye opening |
| flicker | ~0.9-1.2 s, irregular stops | every flame (FLICK) |
| quick | 0.56 s | stickman walk cycle, wing flaps |
| slow | 9-11 s | watcher cycle (head turn + burning eyes) |
| crawl | 5-8 s rise / 22-38 s travel | embers, crows, smoke pass |

Rules kept: transform + opacity only; every entrance has an exit;
stagger in the 0.05-0.10 ratio band; `@media (prefers-reduced-motion:
reduce)` disables all animation.

Palette: black `#07070a`, charcoal silhouettes, ember orange `#ff6a00`,
flame gold `#ffb347`, pale core `#ffe9b0`. The handle is set in a flame
gradient (core → gold → ember). Red survives only inside the glitch
slices' timing — the slices themselves are cream and ember now.

## The watcher cycle (shared behaviour)

Same 11 s choreography as v3, defined once in the generator (`WATCH`):
stillness → breathing → head turns toward the viewer (46-60%) → eyes
burn, hold → eyes go dark, head returns → stillness. Reused in the
banner, the brazier, and the-watcher.

## Scenes

1. **inferno-banner** — ember moon behind drifting smoke, a crow
   crossing, the watcher on the hill, the handle in flame gradient
   glitching in slices, a terminal typing `> forged in fire, hunting in
   the dark_`, embers rising over a full-width line of flickering fire.
2. **brazier** — an iron brazier with a tall flame, sparks rising, warm
   glow pulsing; the broad watcher stands beside it, running the cycle.
3. **watcher-eyes** — sharp slanted eyes, burning orange pupils with
   pale cores, small flames flickering above the brows, embers drifting
   up, slow heavy blink.
4. **flame-divider** — a charred line, a cluster of three flames in the
   middle, single flames at the sides, glowing line-ends, rising embers.
5. **shadow-walk** — the stickman walks through embers; his shadow walks
   out of sync, and halfway across two burning eyes open *inside the
   shadow* and look back. The unique one.
6. **the-watcher** — the broad watcher on a hill split by pulsing lava
   cracks, embers rising around him, ember moon, one crow late.
7. **wolf** — an angular wolf on a rock under the ember moon: head
   throws back to howl on a 9 s cycle, a puff of ember breath escapes,
   tail sways, one eye burns.
8. **rooftop** — black skyline, flickering orange windows, one rooftop
   openly burning (flames + rising smoke), the watcher on the tallest
   roof with his coat fluttering.
9. **embers** — dark smoke layers counter-drifting through rising
   embers; far behind them a small figure walks with two burning eyes,
   half hidden, never hurrying.

The contribution snake is on fire too: `snake.yml` passes
`color_snake=#ff6a00` and ember-ramp `color_dots` for both palettes.

## v5 — api neraka (hellfire pass, same day)

The user pushed the vibe further: "vibes api neraka yang membara"
(blazing hellfire). Same set, intensified, no new files:

- The watcher grows **horns and a cloak** (one `watcher()` change, so he
  upgrades in the banner, brazier, and the-watcher at once) and stands
  silhouetted in front of a **burning hell gate** on the banner hill.
- The banner moon becomes a **ring-of-fire eclipse** (annular, gradient
  ring, black core) and the fire line becomes a **lava lake**: gradient
  band, pulsing bubbles, fewer but larger flames on its surface.
- the-watcher gets **lava flows** pouring from beneath the watcher's
  feet; the divider lines turn molten (pulsing ember); the wolf grows a
  **flame mane** and a flame tail-tip; a second rooftop catches fire;
  the closing strip gains falling **ash** over the smoke and embers.

## v5.1 — realistic fire (same day)

The user asked for the fire itself to look more realistic ("cari yang
lebih realistis"). Researched first (dev.to's SVG fire work + layered
CSS flame studies), then rebuilt `flame()` once — every scene inherits:

- Irregular multi-tongue path instead of the symmetric teardrop; no two
  tongues the same height.
- Bottom-anchored radial gradient: white-hot core → gold → orange →
  deep red edge (real flames are a white-to-orange-to-dark transition,
  not flat yellow/orange).
- `feTurbulence` + `feDisplacementMap` (fractalNoise 0.035/0.11, scale
  13) tearing the flame edges, applied only at s >= 0.7 where it reads.
- A blurred glow copy behind each flame, pulsing on its own slow cycle.
- Smoke wisps rising and fading above the brazier and the hell gate.
