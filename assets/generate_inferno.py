#!/usr/bin/env python3
"""Inferno set v4 for the 0xABCD01 profile README.

Direction from the user (2026-11-26), after the v3 seram set:
"yang seram dark laki banget, terus yang berapi-api dan unik" — seriously
dark, very masculine, on fire, and unique. So v3's watcher stays, but he
is rebuilt broader (wide shoulders, thick strokes, wide stance), the
palette goes black + ember, his eyes burn orange instead of glowing red,
and fire runs through every scene: a fire line under the banner, a
brazier, lava cracks in the hill, a burning rooftop, rising embers
everywhere, a howling wolf, and a shadow whose eyes burn back at you.
Still no horror: no ghosts, no gore, no jumpscare. Fire and darkness.

Motion (user's motion skills): personality TENSE + FIERCE. The watcher
keeps his slow 11 s cycle; fire is the fast layer — flame flicker is
irregular (three uneven keyframe stops, ~1 s, per-flame duration/delay),
embers rise at crawl speed and fade. Transform + opacity only,
prefers-reduced-motion disables everything.
"""
import os

ASSETS = os.path.dirname(os.path.abspath(__file__))

BG = "#07070a"; PANEL = "#0a0a0e"; INK = "#030304"; SIL = "#101016"; SIL2 = "#1d1d26"
CREAM = "#ece5d3"; MOON = "#e9dfc4"; LAV = "#b9b2cc"; SAGE = "#93a58c"
GOLD = "#a8894f"; EMBER = "#ff6a00"; FLAME = "#ffb347"; CORE = "#ffe9b0"; BURN = "#ff8a3d"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

SMOOTH = "cubic-bezier(0.22,1,0.36,1)"
SINE = "cubic-bezier(0.37,0,0.63,1)"
SHARP = "cubic-bezier(0.4,0,0.2,1)"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

def svg(w, h, body, title, desc, style, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<defs>{defs}</defs><style>{style}{REDUCED}</style>{body}</svg>\n')

def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print("wrote", name, len(content))

TWINKLE = "@keyframes tw{0%,100%{opacity:.1}50%{opacity:.45}} .tw{animation:tw 4.4s " + SINE + " infinite}"
FLAP = (".flap{transform-box:fill-box;transform-origin:center;animation:flap .6s " + SINE + " infinite}"
        "@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.45)}}")
WATCH = ("@keyframes headturn{0%,38%,68%,100%{transform:translateX(0)}46%,60%{transform:translateX(3px)}}"
         " .headturn{animation:headturn 11s " + SINE + " infinite}"
         "@keyframes eyeglow{0%,40%,64%,100%{opacity:0}47%,58%{opacity:1}}"
         " .eyeglow{animation:eyeglow 11s " + SHARP + " infinite}"
         "@keyframes breathe{0%,100%{transform:scale(1,1)}50%{transform:scale(1.012,1.02)}}"
         " .breathe{transform-box:fill-box;transform-origin:bottom center;animation:breathe 5s " + SINE + " infinite}")
FLICK = ("@keyframes flick{0%,100%{transform:scale(1,1) skewX(0deg)}28%{transform:scale(.95,1.12) skewX(2.5deg)}"
         "57%{transform:scale(1.04,.93) skewX(-2deg)}79%{transform:scale(.98,1.07) skewX(1deg)}}"
         " .flick{transform-box:fill-box;transform-origin:bottom center;animation:flick 1.1s linear infinite}")
EMBER_CSS = ("@keyframes emberrise{0%{transform:translate(0,0);opacity:0}10%{opacity:.95}"
             "55%{transform:translate(7px,-52px)}100%{transform:translate(-5px,-104px);opacity:0}}"
             " .ember{animation:emberrise 6s linear infinite}")

def stars(points, op=0.45):
    out = ""
    for i, (x, y, r) in enumerate(points):
        out += f'<circle class="tw" style="animation-delay:{i*0.83:.2f}s" cx="{x}" cy="{y}" r="{r}" fill="{CREAM}" opacity="{op}"/>'
    return out

def flame(x, y, s=1.0, dur=1.1, delay=0.0):
    p = "M0 0 C -11 -13 -7 -28 0 -42 C 7 -28 11 -13 0 0"
    return (f'<g transform="translate({x} {y}) scale({s})"><g class="flick" style="animation-duration:{dur}s;animation-delay:{delay}s">'
            f'<path d="{p}" fill="{EMBER}"/><path d="{p}" transform="scale(.66)" fill="{FLAME}"/>'
            f'<path d="{p}" transform="scale(.38)" fill="{CORE}"/></g></g>')

def embers(specs):
    out = ""
    for (x, y, r, dur, delay) in specs:
        col = EMBER if (x + r) % 2 else FLAME
        out += (f'<circle class="ember" style="animation-duration:{dur}s;animation-delay:{delay}s" '
                f'cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0"/>')
    return out

def watcher(x, y, s, color=INK):
    """Broad build: wide shoulder bar, angled torso, thick strokes, wide
    stance. Head turns; the eyes burn (orange shell, pale core)."""
    return (f'<g transform="translate({x} {y})"><g class="breathe">'
            f'<path d="M{-15*s} {-27*s} L{15*s} {-27*s} L{21*s} {15*s} L{-21*s} {15*s} Z" fill="{color}"/>'
            f'<g transform="scale({s})" stroke="{color}" stroke-width="5" stroke-linecap="round" fill="none">'
            f'<path d="M-14 -26 L-19 -4 M14 -26 L19 -4"/>'
            f'<path d="M-6 12 L-13 22 M6 12 L13 22"/></g>'
            f'<g class="headturn"><circle cx="0" cy="{-40*s}" r="{10.5*s}" fill="{color}"/>'
            f'<path d="M{-8.5*s} {-47*s} q {-8*s} {-5*s} {-4*s} {-16*s} M{8.5*s} {-47*s} q {8*s} {-5*s} {4*s} {-16*s}" stroke="{color}" stroke-width="{3.4*s}" stroke-linecap="round" fill="none"/>'
            f'<g class="eyeglow" opacity="0"><circle cx="{-3.8*s}" cy="{-40*s}" r="{2.1*s}" fill="{BURN}"/><circle cx="{3.8*s}" cy="{-40*s}" r="{2.1*s}" fill="{BURN}"/>'
            f'<circle cx="{-3.8*s}" cy="{-40*s}" r="{0.9*s}" fill="{CORE}"/><circle cx="{3.8*s}" cy="{-40*s}" r="{0.9*s}" fill="{CORE}"/></g></g>'
            f'</g></g>')

def stickman(color, s=1.0):
    return (f'<g transform="scale({s})" stroke="{color}" stroke-width="3.4" stroke-linecap="round" fill="none">'
            f'<circle cx="0" cy="-35" r="9.5" fill="none"/>'
            f'<line x1="0" y1="-26" x2="0" y2="0"/>'
            f'<g class="legL"><path d="M0 0 L-10 21"/></g><g class="legR"><path d="M0 0 L10 21"/></g>'
            f'<g class="armL"><path d="M0 -22 L-13 -7"/></g><g class="armR"><path d="M0 -22 L13 -7"/></g></g>')

WALK_CSS = (".legL{transform-box:fill-box;transform-origin:100% 0;animation:swA .56s " + SINE + " infinite}"
            ".legR{transform-box:fill-box;transform-origin:0 0;animation:swB .56s " + SINE + " infinite}"
            ".armL{transform-box:fill-box;transform-origin:100% 0;animation:swB .56s " + SINE + " infinite}"
            ".armR{transform-box:fill-box;transform-origin:0 0;animation:swA .56s " + SINE + " infinite}"
            "@keyframes swA{0%,100%{transform:rotate(17deg)}50%{transform:rotate(-17deg)}}"
            "@keyframes swB{0%,100%{transform:rotate(-17deg)}50%{transform:rotate(17deg)}}"
            "@keyframes bobw{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.6px)}} .bobw{animation:bobw .28s " + SINE + " infinite}")

def crow_path(x, y, s, fill):
    return (f'<path d="M{x} {y} q{7*s} {-8*s} {13*s} {-1*s} q{3*s} {-5*s} {6*s} {-5*s} q{3*s} {1*s} {5*s} {5*s} '
            f'q{7*s} {-7*s} {13*s} {-1*s} q{-7*s} {9*s} {-13*s} {3*s} q{-3*s} {-2*s} {-6*s} {-3*s} '
            f'q{-3*s} {1*s} {-5*s} {3*s} q{-6*s} {-5*s} {-13*s} {-3*s} Z" fill="{fill}"/>')

def crow(x, y, s, fill=SIL2):
    return f'<g class="flap">{crow_path(x, y, s, fill)}</g>'

# ------------------------------------------------------------------ banner --
banner_style = TWINKLE + FLAP + WATCH + FLICK + EMBER_CSS + """
@keyframes lavabub{0%,100%{transform:scale(1);opacity:.35}50%{transform:scale(1.5);opacity:.7}} .lavabub{transform-box:fill-box;transform-origin:center;animation:lavabub 3.8s """ + SINE + """ infinite}
""" + f"""
@keyframes moonglow{{0%,100%{{opacity:.35}}50%{{opacity:.6}}}} .mg{{animation:moonglow 6s {SINE} infinite}}
@keyframes smoke1{{0%{{transform:translateX(-26px)}}100%{{transform:translateX(120px)}}}} .smoke1{{animation:smoke1 38s {SINE} infinite alternate}}
@keyframes crowfly1{{0%{{transform:translate(-160px,8px)}}38%{{transform:translate(560px,-14px)}}100%{{transform:translate(1760px,-30px)}}}} .crowfly1{{animation:crowfly1 24s {SINE} infinite}}
@keyframes gl1{{0%,29%,35%,74%,80%,100%{{opacity:0;transform:translateX(0)}}31%,33%{{opacity:.9;transform:translateX(-6px)}}76%,78%{{opacity:.9;transform:translateX(-4px)}}}} .gl1{{animation:gl1 8s linear infinite}}
@keyframes gl2{{0%,29%,35%,74%,80%,100%{{opacity:0;transform:translateX(0)}}31%,33%{{opacity:.75;transform:translateX(6px)}}76%,78%{{opacity:.75;transform:translateX(4px)}}}} .gl2{{animation:gl2 8s linear infinite}}
@keyframes typeout{{0%{{transform:scaleX(0)}}55%,100%{{transform:scaleX(1)}}}} .ty{{transform-origin:88px 0;animation:typeout 7s steps(27) infinite}}
"""
defs = (f'<radialGradient id="moong"><stop offset="0%" stop-color="{FLAME}"/><stop offset="70%" stop-color="{EMBER}"/>'
        f'<stop offset="100%" stop-color="#b34700"/></radialGradient>'
        f'<linearGradient id="firetext" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{CORE}"/>'
        f'<stop offset="45%" stop-color="{FLAME}"/><stop offset="100%" stop-color="{EMBER}"/></linearGradient>'
        f'<linearGradient id="lavagrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{FLAME}"/>'
        f'<stop offset="35%" stop-color="{EMBER}"/><stop offset="100%" stop-color="#6e1a00"/></linearGradient>')
fire_row = "".join(flame(x, 402, s, 0.9 + (i % 4) * 0.17, -i * 0.23) for i, x in enumerate(range(16, 1600, 96)) for s in [0.6 + (i % 3) * 0.22])
lava_lake = (f'<rect x="0" y="398" width="1600" height="22" fill="url(#lavagrad)"/>'
             + "".join(f'<circle class="lavabub" style="animation-delay:{i*0.9:.1f}s" cx="{140+i*210}" cy="409" r="{4+(i%3)}" fill="{CORE}" opacity="0.5"/>' for i in range(7)))
banner_body = f"""
<rect width="1600" height="420" fill="{BG}"/>
<circle class="mg" opacity="0.5" cx="1392" cy="90" r="76" fill="{EMBER}"/>
<circle cx="1392" cy="90" r="55" fill="none" stroke="url(#moong)" stroke-width="11"/>
<circle cx="1392" cy="90" r="47" fill="{BG}"/>
<g class="smoke1"><ellipse cx="1352" cy="76" rx="92" ry="15" fill="{BG}" opacity="0.9"/><ellipse cx="1424" cy="100" rx="74" ry="12" fill="{BG}" opacity="0.82"/></g>
{stars([(90,54,2.0),(230,110,1.4),(380,44,1.8),(560,88,1.3),(740,50,1.9),(920,104,1.4),(1080,40,1.7),(660,150,1.2),(180,190,1.3)], 0.35)}
<g class="crowfly1">{crow(0,74,1.05,INK)}</g>
<path d="M0 420 L0 384 Q 340 350 700 372 T 1600 376 L1600 420 Z" fill="{INK}"/>
<path d="M1096 356 L1096 262 Q1158 224 1220 262 L1220 356 Z" fill="#0d0d12"/>
<path d="M1108 356 L1108 268 Q1158 238 1208 268 L1208 356 Z" fill="url(#moong)" opacity="0.85"/>
{flame(1132,356,0.8,1.0,-0.3)}{flame(1158,356,1.0,0.9,0.0)}{flame(1184,356,0.8,1.1,-0.6)}
{watcher(1158,352,1.35)}
<text class="gl1" opacity="0" x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{CREAM}" clip-path="url(#gslice)">0xABCD01</text>
<text class="gl2" opacity="0" x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{EMBER}" clip-path="url(#gslice2)">0xABCD01</text>
<clipPath id="gslice"><rect x="80" y="118" width="620" height="30"/></clipPath>
<clipPath id="gslice2"><rect x="80" y="158" width="620" height="26"/></clipPath>
<text x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="url(#firetext)">0xABCD01</text>
<text x="92" y="252" font-family="{MONO}" font-size="27" letter-spacing="6" fill="{FLAME}">BUG BOUNTY · PENTEST · OSINT</text>
<g><clipPath id="tc"><rect class="ty" x="88" y="286" width="640" height="40"/></clipPath>
<text clip-path="url(#tc)" x="90" y="318" font-family="{MONO}" font-size="26" fill="{BURN}">&gt; forged in fire, hunting in the dark_</text></g>
{embers([(140,392,2.2,6.5,-1.0),(330,398,1.7,7.4,-3.2),(520,390,2.4,5.8,-2.1),(760,396,1.8,6.9,-4.4),(980,392,2.1,6.2,-0.6),(1240,398,1.7,7.8,-2.8),(1470,390,2.3,6.6,-5.0),(240,404,1.5,8.2,-5.6),(880,404,1.6,7.1,-1.7),(1330,404,1.5,8.6,-3.9),(420,386,1.9,6.0,-2.5),(1080,386,1.9,6.3,-4.9)])}
{lava_lake}
{fire_row}
"""
write("inferno-banner.svg", svg(1600, 420, banner_body, "0xABCD01 inferno banner",
    "A black banner over a line of fire: an ember moon behind smoke, the handle written in flame gradient and glitching, embers rising, and a broad watcher silhouette on the hill whose eyes burn orange for a moment.", banner_style, defs))

# ----------------------------------------------------------------- brazier --
brazier_style = WATCH + FLICK + EMBER_CSS + f"""
@keyframes glowpulse{{0%,100%{{opacity:.14}}50%{{opacity:.24}}}} .glowpulse{{animation:glowpulse 2.6s {SINE} infinite}}
"""
brazier_body = f"""
<rect width="260" height="190" rx="14" fill="{PANEL}"/>
<ellipse class="glowpulse" opacity="0.2" cx="66" cy="96" rx="52" ry="46" fill="{EMBER}"/>
{flame(66,114,1.85,0.95,-0.3)}{flame(48,116,0.9,1.1,-0.7)}{flame(84,116,0.9,1.05,-0.5)}
<path d="M38 116 L94 116 L84 132 L48 132 Z" fill="{SIL2}"/>
<path d="M52 132 L46 152 M80 132 L86 152 M48 152 L84 152" stroke="{SIL2}" stroke-width="3.4" fill="none"/>
{embers([(52,104,1.8,4.6,-0.8),(66,98,1.5,5.4,-2.4),(80,106,1.7,4.9,-3.6),(58,92,1.3,6.1,-1.5)])}
{watcher(188,152,1.08,SIL2)}
<rect y="176" width="260" height="14" fill="{INK}"/>
"""
write("brazier.svg", svg(260, 190, brazier_body, "Brazier",
    "An iron brazier burning with a tall flickering flame and rising embers, and a broad watcher standing beside it whose head turns and whose eyes burn briefly.", brazier_style))

# ------------------------------------------------------------ watcher eyes --
eyes_style = FLICK + EMBER_CSS + f"""
@keyframes slowblink{{0%,42%,58%,100%{{transform:scaleY(1)}}48%,53%{{transform:scaleY(0.06)}}}} .eye2{{transform-box:fill-box;transform-origin:center;animation:slowblink 7s {SINE} infinite}}
@keyframes track{{0%,24%{{transform:translate(-5px,0)}}40%,60%{{transform:translate(5px,0)}}76%,100%{{transform:translate(-5px,0)}}}} .track{{animation:track 7s {SINE} infinite}}
@keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}} .ring{{transform-origin:100px 100px;animation:spin 34s linear infinite}}
"""
eyes_body = f"""
<circle cx="100" cy="100" r="97" fill="{INK}"/>
<circle class="ring" cx="100" cy="100" r="90" fill="none" stroke="{SIL2}" stroke-width="2" stroke-dasharray="8 16"/>
<path d="M58 66 q -10 -6 -6 -22 M142 66 q 10 -6 6 -22" stroke="{SIL2}" stroke-width="5" stroke-linecap="round" fill="none"/>
{flame(72,64,0.5,0.9,-0.2)}{flame(128,64,0.5,1.05,-0.6)}
<path d="M46 80 L95 90 M154 80 L105 90" stroke="#4a4238" stroke-width="6" stroke-linecap="round"/>
<g class="eye2"><path d="M52 94 L92 101 L89 112 L55 106 Z" fill="{CREAM}" opacity="0.94"/>
<path d="M148 94 L108 101 L111 112 L145 106 Z" fill="{CREAM}" opacity="0.94"/>
<g class="track"><circle cx="72" cy="102" r="5.8" fill="{EMBER}"/><circle cx="128" cy="102" r="5.8" fill="{EMBER}"/>
<circle cx="72" cy="102" r="2.3" fill="{CORE}"/><circle cx="128" cy="102" r="2.3" fill="{CORE}"/></g></g>
{embers([(60,150,1.6,5.2,-1.2),(100,158,1.4,6.0,-3.0),(140,150,1.6,5.6,-2.1),(82,164,1.2,6.8,-4.2),(120,164,1.2,6.4,-0.7)])}
<path d="M70 150 Q 100 142 130 150" stroke="{SIL2}" stroke-width="2.4" fill="none" opacity="0.7"/>
"""
write("watcher-eyes.svg", svg(200, 200, eyes_body, "Burning watcher eyes",
    "Sharp slanted eyes in the dark with burning orange pupils, small flames flickering above the brows, embers drifting up, and a slow heavy blink.", eyes_style))

# ------------------------------------------------------------ flame divider --
divider_style = FLICK + EMBER_CSS + """
@keyframes lavapulse{0%,100%{opacity:.45}50%{opacity:.95}} .lavapulse{animation:lavapulse 4.2s """ + SINE + """ infinite}
""" + f"""
@keyframes endglow{{0%,100%{{opacity:.35}}50%{{opacity:.8}}}} .endglow{{animation:endglow 2.8s {SINE} infinite}}
"""
divider_body = f"""
<line class="lavapulse" x1="8" y1="40" x2="318" y2="40" stroke="{EMBER}" stroke-width="2.4"/>
<line class="lavapulse" x1="402" y1="40" x2="712" y2="40" stroke="{EMBER}" stroke-width="2.4"/>
<circle class="endglow" cx="318" cy="40" r="3" fill="{EMBER}"/><circle class="endglow" cx="402" cy="40" r="3" fill="{EMBER}"/>
{flame(120,52,0.55,1.0,-0.4)}{flame(600,52,0.55,1.15,-0.8)}
{flame(338,54,0.95,1.05,-0.2)}{flame(361,56,1.3,0.9,0.0)}{flame(384,54,0.95,1.2,-0.5)}
{embers([(348,44,1.6,4.8,-1.0),(366,40,1.4,5.5,-2.6),(378,46,1.5,5.1,-3.8)])}
"""
write("flame-divider.svg", svg(720, 64, divider_body, "Flame divider",
    "A charred divider line with a cluster of flickering flames in the middle, smaller flames at the sides, and embers rising from the centre.", divider_style))

# -------------------------------------------------------------- shadow walk --
walk_style = TWINKLE + WALK_CSS + EMBER_CSS + f"""
@keyframes walkman{{0%{{transform:translateX(-46px)}}100%{{transform:translateX(716px)}}}} .walkman{{animation:walkman 9s {SMOOTH} infinite}}
@keyframes walkshadow{{0%{{transform:translateX(-88px)}}100%{{transform:translateX(668px)}}}} .walkshadow{{animation:walkshadow 9s {SMOOTH} infinite}}
@keyframes sheyes{{0%,34%,62%,100%{{opacity:0}}40%,56%{{opacity:1}}}} .sheyes{{animation:sheyes 9s {SHARP} infinite}}
"""
walk_body = f"""
<line x1="6" y1="84" x2="714" y2="84" stroke="{LAV}" stroke-width="2.2" stroke-dasharray="2 10" stroke-linecap="round" opacity="0.45"/>
{stars([(140,12,1.3),(420,8,1.1),(640,16,1.3)], 0.3)}
<g transform="translate(0 86)"><g class="walkshadow" opacity="0.4"><g transform="scale(1 -0.34) skewX(-14)">{stickman(INK,1.0)}
<g class="sheyes" opacity="0"><circle cx="-3.4" cy="-35" r="2.4" fill="{BURN}"/><circle cx="3.4" cy="-35" r="2.4" fill="{BURN}"/></g></g></g></g>
<g class="walkman"><g transform="translate(0 60)"><g class="bobw">{stickman(SIL2,1.0)}</g></g></g>
{embers([(180,80,1.6,6.4,-2.0),(360,82,1.4,7.2,-4.1),(540,80,1.6,6.8,-1.2),(660,82,1.3,7.6,-5.2)])}
"""
write("shadow-walk.svg", svg(720, 110, walk_body, "Shadow walk",
    "A stickman walks through rising embers. His flattened shadow walks out of sync behind him, and halfway across, two burning eyes open inside the shadow and look back.", walk_style))

# -------------------------------------------------------------- the watcher --
watcher_style = TWINKLE + FLAP + WATCH + EMBER_CSS + f"""
@keyframes fogdrift2{{0%{{transform:translateX(-20px)}}100%{{transform:translateX(20px)}}}} .fogdrift2{{animation:fogdrift2 12s {SINE} infinite alternate}}
@keyframes lavapulse{{0%,100%{{opacity:.3}}50%{{opacity:.85}}}} .lavapulse{{animation:lavapulse 5s {SINE} infinite}}
@keyframes crowlate{{0%{{transform:translate(-120px,4px)}}30%{{transform:translate(180px,-6px)}}55%,100%{{transform:translate(860px,-2px)}}}} .crowlate{{animation:crowlate 22s {SINE} infinite}}
"""
watcher_body = f"""
{stars([(80,16,1.4),(210,26,1.1),(520,12,1.3),(668,22,1.1)], 0.35)}
<circle cx="636" cy="30" r="14" fill="{EMBER}"/><circle cx="630" cy="25" r="2.8" fill="#b34700"/>
<g class="crowlate">{crow(0,44,0.7,SIL2)}</g>
<path d="M0 110 L0 84 Q 200 66 360 78 T 720 82 L720 110 Z" fill="{SIL2}"/>
<path d="M0 110 L0 96 Q 240 84 470 92 T 720 94 L720 110 Z" fill="{SIL}"/>
<path class="lavapulse" d="M120 100 L168 92 L214 99 M470 96 L522 90 L566 97 M300 104 L344 98" stroke="{EMBER}" stroke-width="1.8" fill="none" stroke-linecap="round"/>
<path class="lavapulse" style="animation-delay:-2s" d="M352 82 C 344 92 336 98 326 106 M372 84 C 380 92 388 99 398 107" stroke="{EMBER}" stroke-width="3" fill="none" stroke-linecap="round"/>
{watcher(360,54,1.22)}
{embers([(300,96,1.7,6.2,-1.4),(352,100,1.5,7.0,-3.3),(404,97,1.7,6.6,-2.2),(448,100,1.4,7.5,-4.6),(262,100,1.3,7.9,-5.4)])}
<ellipse class="fogdrift2" cx="360" cy="104" rx="230" ry="6" fill="{LAV}" opacity="0.07"/>
"""
write("the-watcher.svg", svg(720, 110, watcher_body, "The watcher",
    "A broad watcher stands motionless on a hill split by glowing lava cracks, embers rising around him. After a long stillness his head turns and his eyes burn orange, hold, and go dark.", watcher_style))

# --------------------------------------------------------------------- wolf --
wolf_style = EMBER_CSS + FLICK + f"""
@keyframes howl{{0%,26%,58%,100%{{transform:rotate(0deg)}}34%,50%{{transform:rotate(-16deg)}}}} .howl{{transform-box:fill-box;transform-origin:18% 88%;animation:howl 9s {SINE} infinite}}
@keyframes puff{{0%,32%{{transform:translate(0,0);opacity:0}}38%{{opacity:.8}}54%,100%{{transform:translate(26px,-16px);opacity:0}}}} .puff{{animation:puff 9s {SINE} infinite}}
@keyframes tailw{{0%,100%{{transform:rotate(0deg)}}50%{{transform:rotate(4deg)}}}} .tailw{{transform-box:fill-box;transform-origin:100% 20%;animation:tailw 4.4s {SINE} infinite}}
"""
wolf_body = f"""
<circle cx="648" cy="18" r="11" fill="{EMBER}"/><circle cx="643" cy="14" r="2.2" fill="#b34700"/>
<line x1="6" y1="53" x2="714" y2="53" stroke="#2b2b31" stroke-width="2.2"/>
<path d="M268 53 L286 44 L420 44 L438 53 Z" fill="{SIL}"/>
<g transform="translate(300 6)">
<path d="M12 40 L6 47 L20 47 L24 38 Z" fill="{SIL2}"/>
<g class="tailw"><path d="M4 34 L-20 26 L-2 22 L10 28 Z" fill="{SIL2}"/></g>
<path d="M8 36 L14 12 L34 4 L58 8 L66 22 L62 36 L40 40 Z" fill="{SIL2}"/>
<path d="M52 22 L58 47 L50 47 L44 24 Z" fill="{SIL2}"/>
<g class="howl"><path d="M34 6 L44 -8 L54 -2 L58 8 L48 14 L36 13 Z" fill="{SIL2}"/>
<path d="M52 -4 L70 -10 L72 -4 L56 4 Z" fill="{SIL2}"/>
<path d="M42 -6 L44 -16 L50 -7 Z" fill="{SIL2}"/>
<circle cx="47" cy="2" r="1.7" fill="{BURN}"/></g>
<g class="puff" opacity="0"><circle cx="76" cy="-6" r="3.2" fill="{FLAME}"/><circle cx="85" cy="-10" r="2.2" fill="{EMBER}"/><circle cx="93" cy="-13" r="1.5" fill="{CORE}"/></g>
{flame(30,10,0.42,1.0,-0.3)}{flame(44,6,0.5,0.9,-0.6)}{flame(-16,30,0.4,1.1,-0.9)}
</g>
{embers([(150,50,1.5,6.8,-2.2),(520,50,1.5,7.3,-3.7),(600,50,1.3,6.1,-1.1)])}
"""
write("wolf.svg", svg(720, 64, wolf_body, "Wolf",
    "An angular wolf silhouette sits on a rock under an ember moon. Every few seconds it throws its head back to howl, and a small puff of ember breath escapes; its tail sways and its eye burns.", wolf_style))

# ------------------------------------------------------------------ rooftop --
roof_style = TWINKLE + FLAP + FLICK + EMBER_CSS + f"""
@keyframes winflick{{0%,100%{{opacity:.75}}42%{{opacity:.3}}48%{{opacity:.8}}70%{{opacity:.45}}76%{{opacity:.75}}}} .winflick{{animation:winflick 6.4s linear infinite}}
@keyframes flutter{{0%,100%{{transform:rotate(-3deg)}}50%{{transform:rotate(4deg)}}}} .flutter{{transform-box:fill-box;transform-origin:top center;animation:flutter 3.4s {SINE} infinite}}
@keyframes smokerise{{0%{{transform:translate(0,0);opacity:.5}}100%{{transform:translate(16px,-26px);opacity:0}}}} .smokerise{{animation:smokerise 7s {SINE} infinite}}
@keyframes crowroof{{0%{{transform:translate(-130px,2px)}}40%{{transform:translate(330px,-8px)}}100%{{transform:translate(1010px,0)}}}} .crowroof{{animation:crowroof 26s {SINE} infinite}}
"""
def win(x, y, delay):
    return f'<rect class="winflick" style="animation-delay:{delay}s" x="{x}" y="{y}" width="7" height="10" fill="{FLAME}"/>'
roof_body = f"""
<circle cx="806" cy="24" r="14" fill="{EMBER}"/><circle cx="800" cy="19" r="2.8" fill="#b34700"/>
{stars([(120,16,1.4),(300,24,1.1),(520,12,1.3),(660,26,1.0)], 0.35)}
<g class="crowroof">{crow(0,30,0.72,SIL)}</g>
<g fill="{SIL}">
<rect x="30" y="66" width="86" height="74"/><rect x="140" y="48" width="70" height="92"/>
<rect x="232" y="78" width="96" height="62"/><rect x="352" y="38" width="76" height="102"/>
<rect x="452" y="62" width="92" height="78"/><rect x="568" y="44" width="68" height="96"/>
<rect x="660" y="74" width="88" height="66"/><rect x="770" y="56" width="80" height="84"/>
</g>
{win(52,84,-1.2)}{win(168,66,-3.4)}{win(258,94,-2.1)}{win(376,58,-4.6)}{win(592,62,-2.9)}{win(688,92,-5.2)}{win(796,74,-1.8)}{win(86,106,-4.1)}
<ellipse class="smokerise" cx="498" cy="34" rx="20" ry="7" fill="#26262e"/>
<ellipse class="smokerise" style="animation-delay:-3.5s" cx="176" cy="22" rx="14" ry="5" fill="#26262e"/>
{flame(164,48,0.55,1.0,-0.4)}{flame(180,48,0.7,0.92,-0.15)}{flame(194,48,0.55,1.08,-0.7)}
{flame(478,62,0.62,0.95,-0.2)}{flame(498,62,0.8,1.1,-0.55)}{flame(518,62,0.62,1.0,-0.8)}
<g transform="translate(390 38)"><g class="flutter"><path d="M-3 -24 L9 -24 L13 0 L-6 0 Z" fill="{INK}"/></g>
<g stroke="{INK}" stroke-width="3.4" stroke-linecap="round"><line x1="0" y1="-24" x2="0" y2="-2"/><line x1="0" y1="-2" x2="-7" y2="0"/><line x1="0" y1="-2" x2="7" y2="0"/></g>
<circle cx="0" cy="-31" r="7.5" fill="{INK}"/></g>
{embers([(610,120,1.6,6.6,-2.4),(700,126,1.4,7.4,-4.0),(180,124,1.5,7.0,-1.6)])}
"""
write("rooftop.svg", svg(880, 140, roof_body, "Rooftop watcher",
    "A black skyline under an ember moon. One rooftop burns with flickering flames and rising smoke, windows flicker orange, and a lone figure stands on the tallest roof, coat fluttering, watching.", roof_style))

# ------------------------------------------------------------------- embers --
mist_style = EMBER_CSS + WALK_CSS + f"""
@keyframes drift1{{from{{transform:translateX(0)}}to{{transform:translateX(-360px)}}}} .d1{{animation:drift1 34s {SINE} infinite}}
@keyframes drift2{{from{{transform:translateX(-360px)}}to{{transform:translateX(0)}}}} .d2{{animation:drift2 46s {SINE} infinite}}
@keyframes farwalk{{0%{{transform:translateX(-40px)}}100%{{transform:translateX(760px)}}}} .farwalk{{animation:farwalk 30s {SINE} infinite}}
@keyframes farpulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}} .farpulse{{animation:farpulse 3.4s {SINE} infinite}}
@keyframes ashfall{{0%{{transform:translate(0,-6px);opacity:0}}18%{{opacity:.5}}100%{{transform:translate(-16px,64px);opacity:0}}}} .ashfall{{animation:ashfall 9s linear infinite}}
"""
smoke_path = lambda y, op: (f'<path d="M0 {y} Q 90 {y-16} 180 {y} T 360 {y} T 540 {y} T 720 {y} T 900 {y} T 1080 {y} L1080 84 L0 84 Z" fill="#17171e" opacity="{op}"/>')
mist_body = f"""
<g class="d1">{smoke_path(34, 0.85)}</g>
<g class="farwalk" opacity="0.6"><g transform="translate(0 46)">{stickman(INK,0.8)}
<g class="farpulse"><circle cx="-2.7" cy="-28" r="1.3" fill="{BURN}"/><circle cx="2.7" cy="-28" r="1.3" fill="{BURN}"/></g></g></g>
<g class="d2">{smoke_path(56, 0.9)}</g>
{embers([(120,74,1.7,5.8,-1.0),(250,78,1.5,6.6,-3.1),(390,74,1.8,6.1,-2.0),(520,78,1.5,7.0,-4.3),(650,74,1.6,6.4,-0.5),(70,80,1.3,7.5,-5.0),(590,80,1.3,7.8,-2.7)])}
<g class="d1" style="animation-duration:52s">{smoke_path(74, 0.95)}</g>
<g fill="#8f8f99"><circle class="ashfall" style="animation-delay:-1s" cx="150" cy="6" r="1.6"/><circle class="ashfall" style="animation-delay:-4s" cx="330" cy="2" r="1.3"/><circle class="ashfall" style="animation-delay:-6.5s" cx="520" cy="8" r="1.7"/><circle class="ashfall" style="animation-delay:-2.8s" cx="660" cy="4" r="1.4"/></g>
"""
write("embers.svg", svg(720, 84, mist_body, "Embers",
    "Dark smoke layers drift against each other through rising embers, and far behind them a small figure walks with two burning eyes, half hidden, never hurrying.", mist_style))

print("done")
