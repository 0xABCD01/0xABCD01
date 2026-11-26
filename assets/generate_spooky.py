#!/usr/bin/env python3
"""Spooky-cute SVG set for the 0xABCD01 profile README — motion v2.

Original choreography, designed with the user's installed motion skills:

- motion-design (LottieFiles): Playful personality archetype, three motion
  layers per scene (primary / secondary / ambient), Disney anticipation +
  squash-and-stretch + follow-through, arcs instead of straight lines,
  emotion map (surprise = ease-out-expo pop, calm = sine ease-in-out).
- motion-foundations: one token system for every file (below), transform +
  opacity only, prefers-reduced-motion kills all transforms.
- motion-patterns: stagger delays stay in the 0.05-0.10 ratio band, every
  entrance also defines its exit.
- motion-advanced: SVG path draw-on (the pumpkin vine), text reveal
  (terminal line), infinite loops kept cheap (transform/opacity only).

Motion tokens (CSS translation of the skills' token map):
  signature easing : cubic-bezier(0.34, 1.56, 0.64, 1)  ease-out-back, playful overshoot
  smooth           : cubic-bezier(0.22, 1, 0.36, 1)      entrances, decelerate
  sine             : cubic-bezier(0.37, 0, 0.63, 1)      ambient loops, gas/fog (2x duration)
  sharp            : cubic-bezier(0.4, 0, 0.2, 1)        exits, flicker cuts
  duration palette : quick 0.9s (hops, flaps) / standard 3.6s (bobs, sways)
                     / slow 7-10s (primary story cycles) / crawl 16-24s (ambient travel)

Micro-story of the set: a ghost haunts the profile. It floats by the house,
gets startled by the lightning, peeks from the attic, chases a bug and shouts
BOO!, hides behind a tombstone, and glides through the fog at the bottom.
"""
import os

ASSETS = os.path.dirname(os.path.abspath(__file__))

NAVY = "#16213a"; NAVY2 = "#1f2c4d"; DARK = "#0d1526"
CREAM = "#f8f1e6"; MOON = "#f6e3b4"; LAV = "#c9c3d9"; SAGE = "#a9b9a4"
GOLD = "#c3a36a"; ORANGE = "#e07b39"; ORANGE_L = "#f2a65a"; GHOST = "#f4efe4"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

BACK = "cubic-bezier(0.34,1.56,0.64,1)"
SMOOTH = "cubic-bezier(0.22,1,0.36,1)"
SINE = "cubic-bezier(0.37,0,0.63,1)"
SHARP = "cubic-bezier(0.4,0,0.2,1)"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

def svg(w, h, body, title, desc, style):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{style}{REDUCED}</style>{body}</svg>\n')

def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print("wrote", name, len(content))

def bat_path(x, y, s, fill=DARK):
    return (f'<path d="M{x} {y} q{6*s} {-7*s} {12*s} 0 q{3*s} {-5*s} {6*s} {-5*s} '
            f'q{3*s} 0 {6*s} {5*s} q{6*s} {-7*s} {12*s} 0 q{-6*s} {9*s} {-12*s} {3*s} '
            f'q{-3*s} {-2*s} {-6*s} {-3*s} q{-3*s} {1*s} {-6*s} {3*s} q{-6*s} {-6*s} {-12*s} {-3*s} Z" fill="{fill}"/>')

def bat(x, y, s, fill=DARK):
    """Bat with flapping wings (secondary layer, quick token)."""
    return (f'<g class="flap">{bat_path(x, y, s, fill)}</g>')

FLAP = (".flap{transform-box:fill-box;transform-origin:center;animation:flap .55s " + SINE + " infinite}"
        "@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.5)}}")

def ghost(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M0 -26 C -16 -26 -22 -12 -22 2 L -22 26 L -15 19 L -8 26 L 0 19 L 8 26 L 15 19 L 22 26 L 22 2 C 22 -12 16 -26 0 -26 Z" fill="{GHOST}"/>'
            f'<circle cx="-8" cy="-4" r="3.2" fill="{NAVY}"/><circle cx="8" cy="-4" r="3.2" fill="{NAVY}"/>'
            f'<ellipse cx="0" cy="5" rx="4" ry="5.5" fill="{NAVY}"/>'
            f'<circle cx="-14" cy="3" r="3.4" fill="{ORANGE_L}" opacity="0.55"/><circle cx="14" cy="3" r="3.4" fill="{ORANGE_L}" opacity="0.55"/></g>')

def stars(points):
    out = ""
    for i, (x, y, r) in enumerate(points):
        out += f'<circle class="tw" style="animation-delay:{i*0.63:.2f}s" cx="{x}" cy="{y}" r="{r}" fill="{CREAM}"/>'
    return out

TWINKLE = "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.4s " + SINE + " infinite}"

def stickman(color=CREAM, s=1.0):
    """Jointed stickman: legs/arms swing from the hip/shoulder pivots
    (transform-box: fill-box, origin on the joint), opposite-phase walk cycle."""
    return (f'<g transform="scale({s})" stroke="{color}" stroke-width="3.4" stroke-linecap="round" fill="none">'
            f'<circle cx="0" cy="-35" r="9.5" fill="none"/>'
            f'<line x1="0" y1="-26" x2="0" y2="0"/>'
            f'<g class="legL"><path d="M0 0 L-10 21"/></g>'
            f'<g class="legR"><path d="M0 0 L10 21"/></g>'
            f'<g class="armL"><path d="M0 -22 L-13 -7"/></g>'
            f'<g class="armR"><path d="M0 -22 L13 -7"/></g></g>')

WALK_CSS = (".legL{transform-box:fill-box;transform-origin:100% 0;animation:swA .56s " + SINE + " infinite}"
            ".legR{transform-box:fill-box;transform-origin:0 0;animation:swB .56s " + SINE + " infinite}"
            ".armL{transform-box:fill-box;transform-origin:100% 0;animation:swB .56s " + SINE + " infinite}"
            ".armR{transform-box:fill-box;transform-origin:0 0;animation:swA .56s " + SINE + " infinite}"
            "@keyframes swA{0%,100%{transform:rotate(17deg)}50%{transform:rotate(-17deg)}}"
            "@keyframes swB{0%,100%{transform:rotate(-17deg)}50%{transform:rotate(17deg)}}")

# ------------------------------------------------------------------ banner --
# Primary: ghost floats on an arc, startled by the lightning (squash -> stretch -> settle).
# Secondary: bats flap across on curved paths, windows flicker, terminal types itself.
# Ambient: moon breathing glow, staggered twinkles, flash every 9s.
banner_style = TWINKLE + FLAP + """
@keyframes moonglow{0%,100%{opacity:.3}50%{opacity:.65}} .mg{animation:moonglow 5s SINE infinite}
@keyframes drift{0%,100%{transform:translate(0,0) rotate(-2deg)}30%{transform:translate(10px,-14px) rotate(2deg)}60%{transform:translate(-6px,-7px) rotate(-1deg)}} .drift{animation:drift 3.6s SINE infinite}
@keyframes startle{0%,58%,74%,100%{transform:scale(1,1) translateY(0)}62%{transform:scale(1.16,.8) translateY(5px)}66%{transform:scale(.9,1.14) translateY(-15px)}70%{transform:scale(1.04,.96) translateY(-3px)}} .startle{transform-box:fill-box;transform-origin:bottom center;animation:startle 9s SHARP infinite}
@keyframes fly1{0%{transform:translate(-180px,10px)}35%{transform:translate(520px,-16px)}70%{transform:translate(1150px,8px)}100%{transform:translate(1780px,-40px)}} .fly1{animation:fly1 17s SINE infinite}
@keyframes fly2{0%{transform:translate(-140px,-6px)}40%{transform:translate(700px,22px)}100%{transform:translate(1740px,-18px)}} .fly2{animation:fly2 23s SINE infinite;animation-delay:-9s}
@keyframes flick{0%,100%{opacity:1}8%{opacity:.25}12%{opacity:1}46%{opacity:1}50%{opacity:.35}54%{opacity:1}78%{opacity:.5}82%{opacity:1}} .fl{animation:flick 4.2s linear infinite}
@keyframes flick2{0%,100%{opacity:.9}30%{opacity:.2}36%{opacity:.95}64%{opacity:.4}70%{opacity:.9}} .fl2{animation:flick2 5.1s linear infinite;animation-delay:-1.7s}
@keyframes flash{0%,60%,66%,100%{opacity:0}62%,64%{opacity:.5}} .flash{animation:flash 9s linear infinite}
@keyframes bolt{0%,60%,66%,100%{opacity:0}62%,64%{opacity:.95}} .bolt{animation:bolt 9s linear infinite}
@keyframes typeout{0%{transform:scaleX(0)}55%,100%{transform:scaleX(1)}} .ty{transform-origin:88px 0;animation:typeout 7s steps(26) infinite}
@keyframes sway{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}} .sway{transform-box:fill-box;transform-origin:top center;animation:sway 4.5s SINE infinite}
""".replace("SINE", SINE).replace("SHARP", SHARP)
house = f"""
<g>
  <path d="M1150 420 L1150 250 L1235 190 L1320 250 L1320 420 Z" fill="{DARK}"/>
  <path d="M1128 252 L1235 176 L1342 252 L1328 252 L1235 188 L1142 252 Z" fill="{NAVY2}"/>
  <rect x="1218" y="150" width="34" height="52" fill="{DARK}"/>
  <path d="M1210 152 L1235 128 L1260 152 Z" fill="{NAVY2}"/>
  <rect class="fl" x="1227" y="162" width="16" height="20" rx="8" fill="{ORANGE_L}"/>
  <rect class="fl2" x="1172" y="282" width="26" height="34" rx="3" fill="{ORANGE}"/>
  <rect class="fl" style="animation-delay:-2.1s" x="1272" y="282" width="26" height="34" rx="3" fill="{ORANGE_L}"/>
  <rect x="1222" y="330" width="26" height="90" rx="12" fill="{NAVY2}"/>
  <circle cx="1241" cy="378" r="2.6" fill="{GOLD}"/>
</g>"""
banner_body = f"""
<rect width="1600" height="420" fill="{NAVY}"/>
<rect class="flash" width="1600" height="420" fill="#e8ecff" opacity="0"/>
<circle class="mg" cx="1420" cy="88" r="86" fill="{MOON}"/>
<circle cx="1420" cy="88" r="58" fill="{MOON}"/>
<circle cx="1400" cy="72" r="9" fill="#ecd29a"/><circle cx="1440" cy="104" r="6" fill="#ecd29a"/>
{stars([(90,60,2.6),(210,120,1.8),(360,48,2.2),(520,96,1.6),(700,52,2.4),(880,110,1.7),(1020,44,2.1),(640,150,1.5),(150,210,1.6),(980,170,1.8),(420,170,1.5),(760,190,1.4)])}
<g class="fly1">{bat(0,84,1.15,NAVY2)}</g>
<g class="fly2">{bat(0,150,0.8,NAVY2)}</g>
<path class="bolt" opacity="0" d="M1046 30 L1018 84 L1038 84 L1006 142 L1058 76 L1036 76 L1062 30 Z" fill="{MOON}"/>
{house}
<path d="M0 420 L0 372 Q 300 338 620 366 T 1150 360 L1600 380 L1600 420 Z" fill="{DARK}"/>
<g class="drift"><g class="startle">{ghost(1062,318,1.25)}</g></g>
<g class="sway">{bat_path(300,352,0.9,DARK)}</g>
<text x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{CREAM}">0xABCD01</text>
<text x="92" y="252" font-family="{MONO}" font-size="27" letter-spacing="6" fill="{GOLD}">BUG BOUNTY · PENTEST · OSINT</text>
<g><clipPath id="tc"><rect class="ty" x="88" y="286" width="560" height="40"/></clipPath>
<text clip-path="url(#tc)" x="90" y="318" font-family="{MONO}" font-size="26" fill="{SAGE}">$ boo. found your bug_</text></g>
<circle cx="118" cy="368" r="4" fill="{ORANGE}"/><circle cx="170" cy="360" r="3" fill="{LAV}"/><circle cx="228" cy="370" r="3.4" fill="{GOLD}"/>
<path d="M118 368 L170 360 L228 370" stroke="{LAV}" stroke-width="1.3" opacity="0.55" fill="none"/>
"""
write("haunted-banner.svg", svg(1600, 420, banner_body, "0xABCD01 haunted banner",
    "A haunted night banner: a glowing full moon, flapping bats, a flickering haunted house, and a cute ghost that floats on an arc and jumps when the lightning strikes.", banner_style))

# ------------------------------------------------------------ haunted house --
# Primary: attic ghost peek with anticipation (crouch, overshoot rise, settle, exit).
# Secondary: spider elastic drop, door glow breathing. Ambient: flicker, bat, twinkles.
hh_style = TWINKLE + FLAP + f"""
@keyframes peek{{0%,14%{{transform:translateY(27px) scale(1,1);opacity:0}}20%{{transform:translateY(29px) scale(1.12,.82);opacity:1}}32%{{transform:translateY(-4px) scale(.94,1.08);opacity:1}}38%,60%{{transform:translateY(0) scale(1,1);opacity:1}}72%,100%{{transform:translateY(27px) scale(1,1);opacity:0}}}} .peek{{animation:peek 7s {SHARP} infinite}}
@keyframes dangle{{0%,18%{{transform:translateY(0)}}44%{{transform:translateY(33px)}}50%{{transform:translateY(29px)}}56%,82%{{transform:translateY(31px)}}100%{{transform:translateY(0)}}}} .dangle{{animation:dangle 6s {BACK} infinite}}
@keyframes legs{{0%,100%{{transform:rotate(-5deg)}}50%{{transform:rotate(5deg)}}}} .legs{{transform-box:fill-box;transform-origin:center;animation:legs .5s {SINE} infinite}}
@keyframes flick{{0%,100%{{opacity:1}}10%{{opacity:.25}}14%{{opacity:1}}52%{{opacity:.35}}58%{{opacity:1}}}} .fl{{animation:flick 4.4s linear infinite}}
@keyframes flyh{{0%{{transform:translate(-40px,6px)}}45%{{transform:translate(120px,-8px)}}100%{{transform:translate(300px,2px)}}}} .flyh{{animation:flyh 11s {SINE} infinite}}
@keyframes bob{{0%,100%{{transform:translate(0,0) rotate(-2deg)}}50%{{transform:translate(3px,-7px) rotate(2deg)}}}} .bob{{animation:bob 3.6s {SINE} infinite}}
@keyframes doorglow{{0%,100%{{opacity:.25}}50%{{opacity:.6}}}} .doorglow{{animation:doorglow 3.6s {SINE} infinite}}
"""
hh_body = f"""
<rect width="260" height="190" rx="14" fill="{NAVY}"/>
<circle cx="222" cy="34" r="17" fill="{MOON}"/><circle cx="215" cy="28" r="3.4" fill="#ecd29a"/>
{stars([(24,26,1.7),(58,48,1.3),(96,22,1.5),(150,40,1.2),(36,84,1.2)])}
<g class="flyh">{bat(0,58,0.62,NAVY2)}</g>
<path d="M52 178 L52 96 L130 44 L208 96 L208 178 Z" fill="{DARK}"/>
<path d="M40 98 L130 36 L220 98 L208 98 L130 48 L52 98 Z" fill="{NAVY2}"/>
<rect x="114" y="16" width="32" height="34" fill="{DARK}"/>
<clipPath id="attic"><rect x="121" y="24" width="18" height="22" rx="8"/></clipPath>
<rect x="121" y="24" width="18" height="22" rx="8" fill="{ORANGE}"/>
<g clip-path="url(#attic)"><g class="peek" opacity="0">{ghost(130,38,0.34)}</g></g>
<rect class="fl" x="70" y="112" width="22" height="28" rx="3" fill="{ORANGE_L}"/>
<rect class="fl" style="animation-delay:-2.2s" x="168" y="112" width="22" height="28" rx="3" fill="{ORANGE}"/>
<rect class="doorglow" x="119" y="128" width="22" height="50" rx="10" fill="{ORANGE_L}"/>
<rect x="119" y="128" width="22" height="50" rx="10" fill="{NAVY2}" opacity="0.72"/><circle cx="135" cy="154" r="2" fill="{GOLD}"/>
<g class="dangle"><line x1="206" y1="86" x2="206" y2="112" stroke="{LAV}" stroke-width="1.2"/>
<g transform="translate(206 120)"><g class="legs"><path d="M-5 -3 L-13 -8 M-6 0 L-14 0 M-5 3 L-12 8 M5 -3 L13 -8 M6 0 L14 0 M5 3 L12 8" stroke="{LAV}" stroke-width="1.3" fill="none"/></g>
<circle r="6.5" fill="{DARK}" stroke="{LAV}" stroke-width="1"/>
<circle cx="-2" cy="-1.6" r="1.1" fill="{ORANGE_L}"/><circle cx="2" cy="-1.6" r="1.1" fill="{ORANGE_L}"/></g></g>
<g class="bob">{ghost(34,158,0.55)}</g>
<rect y="178" width="260" height="12" fill="{DARK}"/>
"""
write("haunted-house.svg", svg(260, 190, hh_body, "Haunted house",
    "A small haunted house: a ghost crouches, then pops up in the attic window with an overshoot; a spider drops on an elastic thread, wiggling its legs.", hh_style))

# -------------------------------------------------------------- spooky eyes --
# Primary: pupils track an unseen visitor (left, centre, right, down at the ghost).
# Secondary: ghost bounce with ease-out-back settle. Ambient: staggered blinks, slow ring.
eyes_style = f"""
@keyframes blink{{0%,91%,100%{{transform:scaleY(1)}}94%{{transform:scaleY(0.08)}}97%{{transform:scaleY(1)}}}} .eye{{transform-box:fill-box;transform-origin:center;animation:blink 4.6s {SINE} infinite}}
@keyframes look{{0%,20%{{transform:translate(-4px,0)}}34%,56%{{transform:translate(4px,0)}}70%,86%{{transform:translate(0,3px)}}100%{{transform:translate(-4px,0)}}}} .pupil{{animation:look 5.6s {SINE} infinite}}
@keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}} .ring{{transform-origin:100px 100px;animation:spin 26s linear infinite}}
@keyframes bounce{{0%,100%{{transform:translateY(0) scale(1,1)}}30%{{transform:translateY(2px) scale(1.1,.86)}}55%{{transform:translateY(-9px) scale(.93,1.09)}}75%{{transform:translateY(-2px) scale(1.03,.98)}}}} .bounce{{animation:bounce 3.4s {BACK} infinite}}
"""
def eye_pair(cx, cy, s, delay):
    return (f'<g class="eye" style="animation-delay:{delay}s">'
            f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<ellipse cx="-17" cy="0" rx="13" ry="9" fill="{CREAM}"/><ellipse cx="17" cy="0" rx="13" ry="9" fill="{CREAM}"/>'
            f'<g class="pupil"><circle cx="-17" cy="0" r="4.6" fill="{NAVY}"/><circle cx="17" cy="0" r="4.6" fill="{NAVY}"/></g>'
            f'</g></g>')
eyes_body = f"""
<circle cx="100" cy="100" r="97" fill="{DARK}"/>
<circle class="ring" cx="100" cy="100" r="90" fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="10 14" opacity="0.8"/>
{eye_pair(100,62,1.0,0)}
{eye_pair(72,108,0.72,-1.53)}
{eye_pair(134,116,0.55,-3.06)}
<g class="bounce">{ghost(100,164,0.62)}</g>
"""
write("spooky-eyes.svg", svg(200, 200, eyes_body, "Eyes in the dark",
    "Pairs of eyes blink in a stagger and their pupils track something unseen, glancing down at a small ghost bouncing with a springy settle.", eyes_style))

# -------------------------------------------------------------- ghost chase --
# Story in one 7s cycle: anticipation crouch, chase on hopping arcs, ghost stretches
# as it lunges, bug squashes and escapes, BOO! pops with ease-out-back (surprise).
chase_style = TWINKLE + f"""
@keyframes run{{0%{{transform:translateX(-70px)}}100%{{transform:translateX(760px)}}}} .run{{animation:run 7s {SMOOTH} infinite}}
@keyframes rung{{0%,6%{{transform:translateX(-176px)}}12%{{transform:translateX(-168px)}}100%{{transform:translateX(654px)}}}} .rung{{animation:rung 7s {SMOOTH} infinite}}
@keyframes hop{{0%,100%{{transform:translateY(0) scale(1,1)}}22%{{transform:translateY(-7px) scale(.96,1.05)}}45%{{transform:translateY(0) scale(1.08,.9)}}70%{{transform:translateY(-6px) scale(.97,1.04)}}}} .hop{{animation:hop .9s {SINE} infinite}}
@keyframes lunge{{0%,58%{{transform:scale(1,1) rotate(0deg)}}68%{{transform:scale(1.13,.88) rotate(-4deg)}}76%{{transform:scale(.95,1.07) rotate(2deg)}}84%,100%{{transform:scale(1,1) rotate(0deg)}}}} .lunge{{transform-box:fill-box;transform-origin:bottom center;animation:lunge 7s {SHARP} infinite}}
@keyframes legw{{0%,100%{{transform:rotate(-16deg)}}50%{{transform:rotate(16deg)}}}} .leg{{transform-box:fill-box;transform-origin:top center;animation:legw .32s {SINE} infinite}}
@keyframes boo{{0%,70%{{opacity:0;transform:scale(.5) rotate(4deg)}}79%{{opacity:1;transform:scale(1.12) rotate(-5deg)}}86%{{opacity:1;transform:scale(1) rotate(-3deg)}}95%,100%{{opacity:0;transform:scale(.92) rotate(-3deg)}}}} .boo{{transform-origin:618px 26px;animation:boo 7s {BACK} infinite}}
@keyframes dust{{0%,100%{{opacity:0;transform:translateX(0) scale(.6)}}50%{{opacity:.5}}}} .dust{{animation:dust 1.8s {SINE} infinite}}
@keyframes speed{{0%,55%,100%{{opacity:0}}65%,85%{{opacity:.75}}}} .speed{{animation:speed 7s linear infinite}}
"""
bug = f"""<g class="run"><g transform="translate(0 58)"><g class="hop">
<g class="leg"><path d="M-8 6 L-15 16 M0 8 L-1 18 M8 6 L14 16" stroke="{GOLD}" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>
<ellipse cx="0" cy="0" rx="17" ry="11" fill="{NAVY2}"/><ellipse cx="9" cy="-2" rx="8" ry="7" fill="{GOLD}"/>
<circle cx="12" cy="-4" r="1.8" fill="{DARK}"/>
<path d="M14 -8 Q 22 -16 26 -14 M12 -9 Q 17 -18 22 -18" stroke="{GOLD}" stroke-width="2" fill="none" stroke-linecap="round"/>
</g></g></g>"""
chase_body = f"""
<line x1="6" y1="72" x2="714" y2="72" stroke="{LAV}" stroke-width="2.4" stroke-dasharray="2 10" stroke-linecap="round" opacity="0.7"/>
{stars([(120,16,1.6),(330,10,1.4),(560,18,1.6)])}
<g class="speed"><path d="M636 44 L668 44 M644 56 L672 56" stroke="{ORANGE_L}" stroke-width="3" stroke-linecap="round"/></g>
<g class="rung"><g class="hop"><g class="lunge">{ghost(0,52,0.95)}</g></g></g>
{bug}
<g class="dust"><circle cx="96" cy="76" r="4" fill="{LAV}"/><circle cx="118" cy="79" r="3" fill="{LAV}"/></g>
<text class="boo" opacity="0" x="592" y="34" font-family="{MONO}" font-size="21" font-weight="700" fill="{ORANGE_L}">BOO!</text>
"""
write("ghost-chase.svg", svg(720, 96, chase_body, "Ghost chase",
    "A ghost crouches, then chases a hopping bug, stretches into a lunge, and shouts BOO! with a springy pop as the bug squashes and escapes.", chase_style))

# ------------------------------------------------------------ spider divider --
# Primary: elastic drop (thread stretches, spider overshoots, legs follow through).
spider_style = TWINKLE + f"""
@keyframes drop{{0%,16%{{transform:translateY(0) scale(1,1)}}42%{{transform:translateY(28px) scale(.94,1.07)}}48%{{transform:translateY(24px) scale(1.07,.92)}}54%,80%{{transform:translateY(26px) scale(1,1)}}100%{{transform:translateY(0) scale(1,1)}}}} .drop{{transform-box:fill-box;transform-origin:top center;animation:drop 8s {BACK} infinite}}
@keyframes thread{{0%,16%{{transform:scaleY(1)}}42%,80%{{transform:scaleY(3.17)}}100%{{transform:scaleY(1)}}}} .thread{{transform-origin:360px 0;animation:thread 8s {SINE} infinite}}
@keyframes legf{{0%,38%,100%{{transform:rotate(0deg)}}48%{{transform:rotate(-7deg)}}58%{{transform:rotate(6deg)}}68%{{transform:rotate(-3deg)}}}} .legf{{transform-box:fill-box;transform-origin:center;animation:legf 8s {SINE} infinite}}
"""
spider_body = f"""
<line x1="8" y1="34" x2="330" y2="34" stroke="{GOLD}" stroke-width="1.6" opacity="0.75"/>
<line x1="390" y1="34" x2="712" y2="34" stroke="{GOLD}" stroke-width="1.6" opacity="0.75"/>
<circle class="tw" cx="352" cy="34" r="2.6" fill="{LAV}"/><circle class="tw" style="animation-delay:-1.6s" cx="368" cy="34" r="2.6" fill="{LAV}"/>
<rect class="thread" x="359.4" y="0" width="1.4" height="12" fill="{LAV}"/>
<g class="drop"><g transform="translate(360 12)">
<g class="legf"><path d="M-5 -3 L-14 -9 M-6 0 L-15 0 M-5 3 L-13 9 M5 -3 L14 -9 M6 0 L15 0 M5 3 L13 9" stroke="{CREAM}" stroke-width="1.5" fill="none"/></g>
<circle r="7.5" fill="{NAVY2}" stroke="{CREAM}" stroke-width="1.2"/>
<circle cx="-2.4" cy="-1.8" r="1.3" fill="{ORANGE_L}"/><circle cx="2.4" cy="-1.8" r="1.3" fill="{ORANGE_L}"/>
<path d="M-3 3.4 Q 0 5.4 3 3.4" stroke="{ORANGE_L}" stroke-width="1.2" fill="none"/></g></g>
"""
write("spider-divider.svg", svg(720, 64, spider_body, "Spider divider",
    "A divider line with a spider that drops on a stretching thread, overshoots, wiggles its legs in follow-through, and climbs back up.", spider_style))

# ------------------------------------------------------------ pumpkin pulse --
# Primary: middle pumpkin swaps faces with a pop. Secondary: vine draws itself
# (motion-advanced path draw-on), pumpkins pop in on a wave stagger, then sway.
pump_style = f"""
@keyframes candle{{0%,100%{{opacity:1}}22%{{opacity:.45}}30%{{opacity:1}}58%{{opacity:.6}}66%{{opacity:1}}84%{{opacity:.5}}92%{{opacity:1}}}} .candle{{animation:candle 3.8s linear infinite}}
@keyframes swapA{{0%,44%{{opacity:1}}52%,92%{{opacity:0}}100%{{opacity:1}}}} .swapA{{animation:swapA 7s linear infinite}}
@keyframes swapB{{0%,44%{{opacity:0}}52%,92%{{opacity:1}}100%{{opacity:0}}}} .swapB{{animation:swapB 7s linear infinite}}
@keyframes facepop{{0%,42%{{transform:scale(1)}}50%{{transform:scale(1.1) rotate(-2deg)}}58%,100%{{transform:scale(1)}}}} .facepop{{transform-box:fill-box;transform-origin:center;animation:facepop 7s {BACK} infinite}}
@keyframes swayp{{0%,100%{{transform:rotate(-2.4deg) translateY(0)}}50%{{transform:rotate(2.4deg) translateY(-2px)}}}} .swayp{{transform-box:fill-box;transform-origin:bottom center;animation:swayp 5s {SINE} infinite}}
@keyframes popin{{0%{{transform:scale(0)}}4%{{transform:scale(1.12)}}6%,100%{{transform:scale(1)}}}} .popin{{transform-box:fill-box;transform-origin:bottom center;animation:popin 21s {BACK} infinite}}
@keyframes drawvine{{0%{{stroke-dashoffset:760}}7%,100%{{stroke-dashoffset:0}}}} .drawvine{{stroke-dasharray:760;animation:drawvine 21s {SMOOTH} infinite}}
"""
def pumpkin(cx, delay, extra=""):
    return (f'<g class="popin" style="animation-delay:{delay}s"><g class="swayp" style="animation-delay:{delay*3:.2f}s"><g transform="translate({cx} 34)">'
            f'<path d="M-2 -24 Q 0 -30 5 -31" stroke="{SAGE}" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="27" ry="21" fill="{ORANGE}"/>'
            f'<ellipse cx="0" cy="0" rx="14" ry="20" fill="none" stroke="#c96a2e" stroke-width="2"/>'
            f'<ellipse cx="0" cy="0" rx="25" ry="20" fill="none" stroke="#c96a2e" stroke-width="2"/>'
            f'{extra}</g></g></g>')
face_cute = f'<g class="candle"><path d="M-13 -6 L-7 -13 L-1 -6 Z M13 -6 L7 -13 L1 -6 Z" fill="{MOON}"/><path d="M-13 6 L-8 11 L-3 6 L2 11 L7 6 L12 11 L10 3 L-11 3 Z" fill="{MOON}"/></g>'
face_scary = f'<g class="candle"><path d="M-14 -5 L-6 -12 L-2 -4 Z M14 -5 L6 -12 L2 -4 Z" fill="{DARK}"/><path d="M-12 8 L-7 2 L-2 8 L3 2 L8 8 L12 3 L11 10 L-11 10 Z" fill="{DARK}"/></g>'
mid_faces = f'<g class="facepop"><g class="swapA">{face_cute}</g><g class="swapB">{face_scary}</g></g>'
pump_body = f"""
<path class="drawvine" d="M4 40 Q 90 26 180 38 T 360 38 T 540 38 T 716 36" stroke="{SAGE}" stroke-width="2.2" fill="none" opacity="0.8"/>
{pumpkin(180, 0.9, face_cute)}
{pumpkin(360, 1.05, mid_faces)}
{pumpkin(540, 1.2, face_cute)}
"""
write("pumpkin-pulse.svg", svg(720, 64, pump_body, "Pumpkin row",
    "A vine draws itself across, three jack-o'-lanterns pop in on a wave stagger and sway; their candle faces flicker and the middle one pops between a grin and a scary face.", pump_style))

# ---------------------------------------------------------------- graveyard --
# Primary: ghost rises on an arc with sway, hovers, sinks back (enter + exit defined).
# Secondary: hanging bat pendulum with wing flap. Ambient: gas fog at 2x duration, blinks.
grave_style = TWINKLE + FLAP + f"""
@keyframes rise{{0%,12%{{transform:translate(0,26px) rotate(0deg);opacity:0}}26%{{transform:translate(-4px,-3px) rotate(-3deg);opacity:1}}34%,56%{{transform:translate(3px,-6px) rotate(2deg);opacity:1}}72%,100%{{transform:translate(0,26px) rotate(0deg);opacity:0}}}} .rise{{animation:rise 10s {SINE} infinite}}
@keyframes fogmove{{0%{{transform:translateX(-46px)}}100%{{transform:translateX(46px)}}}} .fogm{{animation:fogmove 18s {SINE} infinite alternate}}
@keyframes fogmove2{{0%{{transform:translateX(38px)}}100%{{transform:translateX(-38px)}}}} .fogm2{{animation:fogmove2 24s {SINE} infinite alternate}}
@keyframes blinkg{{0%,90%,100%{{opacity:1}}94%{{opacity:0}}}} .blinkg{{animation:blinkg 5.4s linear infinite}}
@keyframes hang{{0%,100%{{transform:rotate(6deg)}}50%{{transform:rotate(-6deg)}}}} .hang{{transform-origin:118px 26px;animation:hang 4.2s {SINE} infinite}}
@keyframes shiver{{0%,20%,64%,100%{{transform:translateX(0)}}28%{{transform:translateX(-1.4px)}}34%{{transform:translateX(1.4px)}}40%{{transform:translateX(-1.4px)}}46%{{transform:translateX(1.4px)}}52%{{transform:translateX(-1px)}}58%{{transform:translateX(1px)}}}} .shiver{{animation:shiver 10s linear infinite}}
@keyframes beamf{{0%,100%{{opacity:.28}}48%{{opacity:.34}}52%{{opacity:.18}}56%{{opacity:.3}}}} .beamf{{animation:beamf 10s linear infinite}}
"""
def tomb(x, y, w, h, label="RIP"):
    return (f'<path d="M{x} {y} L{x} {y-h+w/2} Q {x} {y-h} {x+w/2} {y-h} Q {x+w} {y-h} {x+w} {y-h+w/2} L{x+w} {y} Z" fill="#39445f"/>'
            f'<text x="{x+w/2}" y="{y-h+22}" font-family="{MONO}" font-size="10" fill="{LAV}" text-anchor="middle">{label}</text>')
grave_body = f"""
<circle cx="822" cy="26" r="15" fill="{MOON}"/><circle cx="815" cy="21" r="3" fill="#ecd29a"/>
{stars([(180,18,1.5),(330,26,1.3),(520,14,1.6),(660,24,1.3)])}
<path d="M104 118 L104 44 M104 62 L84 48 M104 74 L126 56" stroke="{DARK}" stroke-width="6" stroke-linecap="round" fill="none"/>
<g class="hang">{bat(104,30,0.72,DARK)}</g>
<rect y="116" width="880" height="24" fill="{DARK}"/>
{tomb(180,124,54,58)}
{tomb(420,126,62,66,"BUGS")}
{tomb(640,124,50,52)}
<clipPath id="graveclip"><rect x="0" y="30" width="880" height="90"/></clipPath>
<g clip-path="url(#graveclip)"><g class="rise" opacity="0">{ghost(451,86,0.8)}</g></g>
<g class="blinkg"><circle cx="300" cy="98" r="2.6" fill="{ORANGE_L}"/><circle cx="312" cy="98" r="2.6" fill="{ORANGE_L}"/></g>
<g class="blinkg" style="animation-delay:-2.7s"><circle cx="566" cy="104" r="2.3" fill="{ORANGE_L}"/><circle cx="577" cy="104" r="2.3" fill="{ORANGE_L}"/></g>
<g transform="translate(772 94)"><g class="shiver"><polygon class="beamf" points="-12,-9 -64,-2 -62,13" fill="{GOLD}"/>
{stickman(CREAM, 0.92)}</g></g>
<g class="fogm"><ellipse cx="240" cy="122" rx="150" ry="10" fill="{LAV}" opacity="0.16"/><ellipse cx="620" cy="128" rx="170" ry="9" fill="{LAV}" opacity="0.13"/></g>
<g class="fogm2"><ellipse cx="440" cy="118" rx="130" ry="8" fill="{CREAM}" opacity="0.10"/></g>
"""
write("graveyard.svg", svg(880, 140, grave_body, "Graveyard",
    "A graveyard at night: a ghost rises on a swaying arc from behind a tombstone marked BUGS, hovers, and sinks back; fog drifts slowly and a bat swings upside down from a dead tree.", grave_style))

# ------------------------------------------------------------- stickman hunt --
# Story in 8s: the stickman walks in with a flashlight (jointed walk cycle,
# opposite-phase limbs, body bob), a ghost pops up ahead, he startles back
# (squash, "!!"), then panic-walks past as the ghost sinks away.
hunt_style = TWINKLE + WALK_CSS + f"""
@keyframes walkx{{0%{{transform:translate(-46px,0)}}54%{{transform:translate(322px,0)}}60%{{transform:translate(304px,-9px) scale(1.06,.9)}}66%{{transform:translate(310px,0) scale(1,1)}}100%{{transform:translate(716px,0)}}}} .walkx{{animation:walkx 8s {SMOOTH} infinite}}
@keyframes bobw{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-2.6px)}}}} .bobw{{animation:bobw .28s {SINE} infinite}}
@keyframes beamh{{0%,100%{{transform:rotate(-4deg)}}50%{{transform:rotate(5deg)}}}} .beamh{{transform-box:fill-box;transform-origin:0 50%;animation:beamh 2.2s {SINE} infinite}}
@keyframes popghost{{0%,50%{{transform:translateY(30px);opacity:0}}58%,74%{{transform:translateY(0);opacity:1}}82%,100%{{transform:translateY(30px);opacity:0}}}} .popghost{{animation:popghost 8s {SHARP} infinite}}
@keyframes bang{{0%,56%{{opacity:0;transform:scale(.5) rotate(6deg)}}63%,72%{{opacity:1;transform:scale(1.1) rotate(-6deg)}}78%,100%{{opacity:0;transform:scale(.9)}}}} .bang{{transform-origin:330px 18px;animation:bang 8s {BACK} infinite}}
"""
hunt_body = f"""
<line x1="6" y1="88" x2="714" y2="88" stroke="{LAV}" stroke-width="2.4" stroke-dasharray="2 10" stroke-linecap="round" opacity="0.7"/>
{stars([(90,14,1.5),(250,8,1.3),(610,12,1.5),(690,26,1.2)])}
<g clip-path="url(#huntclip)"><g class="popghost" opacity="0">{ghost(486,58,0.95)}</g></g>
<clipPath id="huntclip"><rect x="430" y="8" width="112" height="82"/></clipPath>
<g class="walkx"><g transform="translate(0 62)"><g class="bobw">
<g class="beamh"><polygon points="13,-9 74,2 72,17" fill="{GOLD}" opacity="0.32"/></g>
{stickman(CREAM, 1.0)}
<rect x="10" y="-13" width="7" height="5" rx="1.6" fill="{ORANGE_L}"/>
</g></g></g>
<text class="bang" opacity="0" x="318" y="26" font-family="{MONO}" font-size="22" font-weight="700" fill="{ORANGE_L}">!!</text>
"""
write("stickman-hunt.svg", svg(720, 110, hunt_body, "Stickman hunt",
    "A stickman with a flashlight walks in with a jointed walk cycle, startles back with a squash when a ghost pops up, then panic-walks past as it sinks away.", hunt_style))

# ---------------------------------------------------------------------- fog --
# Gas material: slowest durations, sine easing, ghost glides a long shallow arc.
fog_style = f"""
@keyframes drift1{{from{{transform:translateX(0)}}to{{transform:translateX(-360px)}}}} .d1{{animation:drift1 30s {SINE} infinite}}
@keyframes drift2{{from{{transform:translateX(-360px)}}to{{transform:translateX(0)}}}} .d2{{animation:drift2 42s {SINE} infinite}}
@keyframes pass{{0%{{transform:translate(-70px,2px) rotate(2deg)}}30%{{transform:translate(190px,-7px) rotate(-2deg)}}62%{{transform:translate(470px,0) rotate(1deg)}}100%{{transform:translate(790px,-8px) rotate(-2deg)}}}} .pass{{animation:pass 16s {SINE} infinite}}
@keyframes bobf{{0%,100%{{transform:translateY(0) scale(1,1)}}50%{{transform:translateY(-5px) scale(.98,1.03)}}}} .bobf{{animation:bobf 2.8s {SINE} infinite}}
@keyframes blinkf{{0%,89%,100%{{opacity:1}}93%{{opacity:0}}}} .blinkf{{animation:blinkf 4.8s linear infinite}}
"""
mist = lambda y, fill, op: (f'<path d="M0 {y} Q 90 {y-16} 180 {y} T 360 {y} T 540 {y} T 720 {y} T 900 {y} T 1080 {y} L1080 84 L0 84 Z" fill="{fill}" opacity="{op}"/>')
fog_body = f"""
<g class="pass"><g class="bobf">{ghost(0,34,0.72)}</g></g>
<g class="blinkf"><circle cx="520" cy="52" r="2.5" fill="{ORANGE_L}"/><circle cx="532" cy="52" r="2.5" fill="{ORANGE_L}"/></g>
<g class="d1">{mist(38, LAV, 0.35)}</g>
<g class="d2">{mist(56, SAGE, 0.4)}</g>
<g class="d1" style="animation-duration:48s">{mist(72, GOLD, 0.35)}</g>
"""
write("fog.svg", svg(720, 84, fog_body, "Rolling fog",
    "Layers of fog drift slowly past each other like gas while a small ghost glides through on a long shallow arc and a pair of eyes blinks from the mist.", fog_style))

print("done")
