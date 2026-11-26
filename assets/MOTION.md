# Motion system — haunted profile set

Original choreography for the animated SVGs in this folder, built with the
motion skills in `~/workspace/custom-skills/` (`motion-design`,
`motion-foundations`, `motion-patterns`, `motion-advanced`). The generator
is `generate_spooky.py`; regenerate with `python3 generate_spooky.py`.

## Personality

Playful (motion-design archetype): 150-300 ms character at loop scale,
ease-out-back overshoot 10-20%, bouncy and cute — the "lucu" half of
lucu-seram. The "seram" half is staging: dark scenes, flicker, lightning,
things that peek and hide.

## Tokens (one system for every file)

| Token | Value | Used for |
|---|---|---|
| signature easing | `cubic-bezier(0.34, 1.56, 0.64, 1)` | pops, bounces, elastic drops |
| smooth | `cubic-bezier(0.22, 1, 0.36, 1)` | entrances, the chase, path draw-on |
| sine | `cubic-bezier(0.37, 0, 0.63, 1)` | ambient loops; fog/gas at 2x duration |
| sharp | `cubic-bezier(0.4, 0, 0.2, 1)` | exits, anticipation cuts |
| duration quick | 0.9 s | hops, wing flaps, leg wiggles |
| duration standard | 3.6 s | bobs, sways, bounces |
| duration slow | 7-10 s | primary story cycles |
| duration crawl | 16-24 s | ambient travel (bats, fog, ghost glide) |

Rules carried over from the skills: transform + opacity only, never layout
properties; every entrance defines its exit; stagger delays stay in the
0.05-0.10 ratio band; spatial movement is never linear (arcs and easing
everywhere — the only linear loops are flicker, the ring spin, and the
typing steps); `@media (prefers-reduced-motion: reduce)` disables all
animation in every file.

## The micro-story

One ghost haunts the whole profile, top to bottom:

1. **haunted-banner** — it floats on an arc beside the house, and jumps
   (squash, stretch, settle) when the lightning strikes at 62% of the 9 s
   cycle. Bats flap across on curved paths; the moon breathes.
2. **haunted-house** — it crouches (anticipation), pops up in the attic
   window with an overshoot, settles, and ducks out. A spider drops on an
   elastic thread beside it, legs wiggling in follow-through.
3. **spooky-eyes** — pupils track an unseen visitor left, right, then down
   at the ghost, which bounces with an ease-out-back settle. Blinks are
   staggered so the eyes never close together.
4. **ghost-chase** — crouch, chase on hopping arcs, a stretched lunge, and
   BOO! popping at 79% with speed lines and dust as secondary motion.
5. **spider-divider** — the drop is one elastic gesture: thread stretches,
   body overshoots and squashes, legs settle last.
6. **pumpkin-pulse** — the vine draws itself (path draw-on), three
   jack-o'-lanterns pop in on a wave stagger and sway; the middle one's
   face pops as it swaps grin ↔ scary.
7. **graveyard** — the ghost rises on a swaying arc from the BUGS
   tombstone, hovers, sinks back. Fog moves at gas speed (2x duration).
8. **fog** — the ghost glides out on a long shallow arc while the mist
   layers counter-drift at 20-30% of its speed.

The contribution graph below the stats is Pac-Man chased by ghosts
(`abozanona/pacman-contribution-graph`, workflow `haunted.yml`) — same
chase story, played on the contribution grid.
