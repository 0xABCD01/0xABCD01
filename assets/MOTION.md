# Motion system — seram set (v3)

Theme, in the user's words: **seram, bukan seram horror**. No haunted
house, no graveyard, no pumpkins, no cute ghost, no jumpscare. Seram here
is eerie and menacing: darkness, stillness, being watched. One watcher
figure recurs through the profile — on the banner hill, at the streetlamp,
on the rooftop, alone in the fog — and crows do the rest.

Built with the motion skills in `~/workspace/custom-skills/`
(`motion-design`, `motion-foundations`, `motion-patterns`,
`motion-advanced`). Generator: `generate_seram.py`
(`python3 generate_seram.py`).

## Personality: TENSE

Re-tuned from v2's Playful archetype. Long durations, overshoot ~0, sine
easing for anything alive. The only fast motion in the whole set is the
glitch cut (100-200 ms windows, sharp easing). Tension comes from
stillness plus one change: a head turns, eyes open, a lamp dips — then
nothing moves again for seconds.

## Tokens

| Token | Value | Used for |
|---|---|---|
| smooth | `cubic-bezier(0.22, 1, 0.36, 1)` | entrances, walks across frame |
| sine | `cubic-bezier(0.37, 0, 0.63, 1)` | living loops; fog/mist at 2x duration |
| sharp | `cubic-bezier(0.4, 0, 0.2, 1)` | glitch cuts, lamp dip, eye opening |
| quick | 0.56 s | stickman walk cycle, wing flaps |
| standard | 3.6-5 s | breathing, moth orbit, coat flutter |
| slow | 9-11 s | watcher cycles (head turn + eyes), lamp cycle |
| crawl | 22-40 s | crow flights, cloud pass, far figure in mist |

Rules kept from the skills: transform + opacity only; every entrance has
an exit; stagger in the 0.05-0.10 ratio band; spatial motion is never
linear except the glitch slices and the ring spin;
`@media (prefers-reduced-motion: reduce)` disables all animation.

Palette: near-black navy `#0b0f1a`, pale moon, dim gold, muted cream.
One red (`#e5484d`) exists in the whole set, used only for eyes, a few
pixels at a time.

## The watcher cycle (shared behaviour)

Every watcher figure runs the same 11 s choreography: stillness →
breathing → the head turns toward the viewer (46-60%) → two red eyes
open, hold → eyes close, head returns → stillness. It is defined once in
the generator (`WATCH`) and reused in the banner, the streetlamp, and
the-watcher, so the figure feels like the same presence everywhere.

## Scenes

1. **dark-banner** — moon behind a slow cloud pass, two crows on curved
   flights, scanlines, the watcher on the hill, and the handle glitching
   in red/lavender slices twice per 8 s cycle. Terminal types
   `> i see the bugs you hide_`.
2. **streetlamp** — the lamp dips once per 7 s (sharp), a moth orbits
   its head, the watcher stands at the edge of the light running the
   watcher cycle.
3. **watcher-eyes** — one pair of sharp slanted eyes; pupils track left,
   right, centre over 7 s; the blink is slow and heavy (closed ~0.7 s);
   a red glint sits in each pupil.
4. **glitch-divider** — the line glitches in red and lavender slices; a
   perched crow tilts its head, flicks its tail, its eye brightens.
5. **shadow-walk** — a stickman walks the frame; his shadow, flattened
   under his feet, walks the same path a half-step behind and never quite
   matches his stride.
6. **the-watcher** — the watcher alone on a foggy hill. Almost nothing
   moves. That is the point.
7. **raven** — a raven on a branch turns its head to look, tail flick,
   feather ruffle; two smaller crows further along, eyes brightening at
   different times.
8. **rooftop** — skyline, a few flickering windows, the watcher on the
   tallest roof with his coat fluttering, fog below, a crow crossing.
9. **mist** — mist layers counter-drift at gas speed; far behind them a
   small dark figure walks through, half hidden, never hurrying.

The contribution graph is the snake again (Platane/snk, `snake.yml`) —
the Pac-Man ghosts belonged to the horror set.
