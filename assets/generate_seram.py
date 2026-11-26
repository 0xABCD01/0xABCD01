#!/usr/bin/env python3
"""Seram set v3 for the 0xABCD01 profile README.

Theme correction from the user (2026-11-26): "seram, bukan seram horror".
So: no haunted house, no graveyard, no pumpkins, no cute ghost, no BOO!.
Seram here is eerie and menacing, not horror — darkness, stillness, being
watched. A lone watcher figure, crows, a streetlamp, glitch cuts, red eyes
that open in the dark, and a shadow that does not quite follow its owner.

Motion system (from the user's motion skills, personality re-tuned):
- motion-design: personality is now TENSE — long durations, overshoot ~0,
  sine easing for anything alive; the only fast motion is the glitch cut
  (sharp, 100-200 ms windows). Tension comes from stillness + one change.
- motion-foundations: same token discipline, transform + opacity only,
  prefers-reduced-motion disables everything.
- motion-patterns: stagger kept in the 0.05-0.10 ratio band.
- motion-advanced: text reveal (terminal), path/figure articulation
  (jointed stickman, pivoting heads).

Tokens:
  signature : cubic-bezier(0.22, 1, 0.36, 1)   smooth, entrances
  sine      : cubic-bezier(0.37, 0, 0.63, 1)   living loops, fog (2x)
  sharp     : cubic-bezier(0.4, 0, 0.2, 1)     glitch cuts, flicker dips
  durations : quick 0.56s walk cycle / standard 3.6-5s breathing
              slow 9-11s watcher cycles / crawl 22-40s travel, clouds
Palette: near-black navy, pale moon, dim gold, and one red (#e5484d) used
only for eyes — a few pixels at a time.
"""
import os

ASSETS = os.path.dirname(os.path.abspath(__file__))

BG = "#0b0f1a"; PANEL = "#0d1322"; INK = "#05080f"; SIL = "#141d31"; SIL2 = "#232f4d"
CREAM = "#e8e2d4"; MOON = "#e9dfc4"; LAV = "#b9b2cc"; SAGE = "#93a58c"
GOLD = "#a8894f"; RED = "#e5484d"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

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

def stars(points, op=0.5):
    out = ""
    for i, (x, y, r) in enumerate(points):
        out += f'<circle class="tw" style="animation-delay:{i*0.83:.2f}s" cx="{x}" cy="{y}" r="{r}" fill="{CREAM}" opacity="{op}"/>'
    return out

TWINKLE = "@keyframes tw{0%,100%{opacity:.12}50%{opacity:.5}} .tw{animation:tw 4.4s " + SINE + " infinite}"
FLAP = (".flap{transform-box:fill-box;transform-origin:center;animation:flap .6s " + SINE + " infinite}"
        "@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.45)}}")
# Watcher behaviour, shared by every figure: long stillness, the head turns
# toward the viewer, the eyes open red, hold, then everything goes still again.
WATCH = ("@keyframes headturn{0%,38%,68%,100%{transform:translateX(0)}46%,60%{transform:translateX(3px)}}"
         " .headturn{animation:headturn 11s " + SINE + " infinite}"
         "@keyframes eyeglow{0%,40%,64%,100%{opacity:0}47%,58%{opacity:1}}"
         " .eyeglow{animation:eyeglow 11s " + SHARP + " infinite}"
         "@keyframes breathe{0%,100%{transform:scale(1,1)}50%{transform:scale(1.012,1.02)}}"
         " .breathe{transform-box:fill-box;transform-origin:bottom center;animation:breathe 5s " + SINE + " infinite}")

def watcher(x, y, s, color=INK, eye_r=1.5):
    """Still silhouette figure. Head is its own group so it can turn."""
    return (f'<g transform="translate({x} {y})"><g class="breathe"><g transform="scale({s})" stroke="{color}" stroke-width="3.6" stroke-linecap="round" fill="none">'
            f'<line x1="0" y1="-25" x2="0" y2="0"/><line x1="0" y1="0" x2="-9" y2="21"/><line x1="0" y1="0" x2="9" y2="21"/>'
            f'<line x1="0" y1="-21" x2="-12" y2="-6"/><line x1="0" y1="-21" x2="12" y2="-6"/></g>'
            f'<g class="headturn"><circle cx="0" cy="{-35*s}" r="{9.5*s}" fill="{color}"/>'
            f'<g class="eyeglow" opacity="0"><circle cx="{-3.4*s}" cy="{-35*s}" r="{eye_r}" fill="{RED}"/><circle cx="{3.4*s}" cy="{-35*s}" r="{eye_r}" fill="{RED}"/></g></g>'
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
banner_style = TWINKLE + FLAP + WATCH + f"""
@keyframes moonglow{{0%,100%{{opacity:.25}}50%{{opacity:.55}}}} .mg{{animation:moonglow 6s {SINE} infinite}}
@keyframes cloudpass{{0%{{transform:translateX(-30px)}}100%{{transform:translateX(150px)}}}} .cloudpass{{animation:cloudpass 40s {SINE} infinite alternate}}
@keyframes crowfly1{{0%{{transform:translate(-160px,8px)}}38%{{transform:translate(560px,-14px)}}100%{{transform:translate(1760px,-30px)}}}} .crowfly1{{animation:crowfly1 24s {SINE} infinite}}
@keyframes crowfly2{{0%{{transform:translate(-120px,0)}}45%{{transform:translate(760px,16px)}}100%{{transform:translate(1720px,-8px)}}}} .crowfly2{{animation:crowfly2 31s {SINE} infinite;animation-delay:-14s}}
@keyframes gl1{{0%,29%,35%,74%,80%,100%{{opacity:0;transform:translateX(0)}}31%,33%{{opacity:.85;transform:translateX(-6px)}}76%,78%{{opacity:.85;transform:translateX(-4px)}}}} .gl1{{animation:gl1 8s linear infinite}}
@keyframes gl2{{0%,29%,35%,74%,80%,100%{{opacity:0;transform:translateX(0)}}31%,33%{{opacity:.7;transform:translateX(6px)}}76%,78%{{opacity:.7;transform:translateX(4px)}}}} .gl2{{animation:gl2 8s linear infinite}}
@keyframes typeout{{0%{{transform:scaleX(0)}}55%,100%{{transform:scaleX(1)}}}} .ty{{transform-origin:88px 0;animation:typeout 7s steps(24) infinite}}
"""
scanlines = "".join(f'<rect x="0" y="{y}" width="1600" height="1" fill="#ffffff" opacity="0.035"/>' for y in range(14, 420, 28))
banner_body = f"""
<rect width="1600" height="420" fill="{BG}"/>
{scanlines}
<circle class="mg" cx="1392" cy="90" r="82" fill="{MOON}"/>
<circle cx="1392" cy="90" r="55" fill="{MOON}"/>
<g class="cloudpass"><ellipse cx="1360" cy="78" rx="86" ry="15" fill="{BG}" opacity="0.88"/><ellipse cx="1420" cy="98" rx="70" ry="12" fill="{BG}" opacity="0.8"/></g>
{stars([(90,54,2.2),(230,110,1.5),(380,44,1.9),(560,88,1.4),(740,50,2.0),(920,104,1.5),(1080,40,1.8),(660,150,1.3),(180,190,1.4)])}
<g class="crowfly1">{crow(0,80,1.05,INK)}</g>
<g class="crowfly2">{crow(0,140,0.75,INK)}</g>
<path d="M0 420 L0 378 Q 340 344 700 368 T 1600 372 L1600 420 Z" fill="{INK}"/>
{watcher(1158,352,1.32)}
<text class="gl1" opacity="0" x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{RED}" clip-path="url(#gslice)">0xABCD01</text>
<text class="gl2" opacity="0" x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{LAV}" clip-path="url(#gslice2)">0xABCD01</text>
<clipPath id="gslice"><rect x="80" y="118" width="620" height="30"/></clipPath>
<clipPath id="gslice2"><rect x="80" y="158" width="620" height="26"/></clipPath>
<text x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{CREAM}">0xABCD01</text>
<text x="92" y="252" font-family="{MONO}" font-size="27" letter-spacing="6" fill="{GOLD}">BUG BOUNTY · PENTEST · OSINT</text>
<g><clipPath id="tc"><rect class="ty" x="88" y="286" width="600" height="40"/></clipPath>
<text clip-path="url(#tc)" x="90" y="318" font-family="{MONO}" font-size="26" fill="{SAGE}">&gt; i see the bugs you hide_</text></g>
"""
write("dark-banner.svg", svg(1600, 420, banner_body, "0xABCD01 dark banner",
    "A dark banner: a pale moon behind drifting cloud, crows crossing, a lone watcher silhouette on a hill whose head turns and whose red eyes open for a moment, and the handle glitching in slices.", banner_style))

# ------------------------------------------------------------- streetlamp --
lamp_style = WATCH + f"""
@keyframes lampglow{{0%,100%{{opacity:.16}}50%{{opacity:.2}}}} .lampglow{{animation:lampglow 5s {SINE} infinite}}
@keyframes lampdip{{0%,49%,55%,100%{{opacity:1}}51%,53%{{opacity:.25}}}} .lampdip{{animation:lampdip 7s linear infinite}}
@keyframes moth{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}} .moth{{transform-origin:64px 44px;animation:moth 3.8s linear infinite}}
@keyframes fogdrift{{0%{{transform:translateX(-14px)}}100%{{transform:translateX(14px)}}}} .fogdrift{{animation:fogdrift 9s {SINE} infinite alternate}}
"""
lamp_body = f"""
<rect width="260" height="190" rx="14" fill="{PANEL}"/>
{stars([(200,24,1.4),(232,58,1.2),(168,40,1.1)])}
<polygon class="lampglow" opacity="0.18" points="64,52 22,178 118,178" fill="{MOON}"/>
<g class="lampdip"><rect x="61" y="46" width="7" height="132" fill="{SIL2}"/>
<path d="M50 48 L79 48 L71 32 L58 32 Z" fill="{SIL2}"/><circle cx="64" cy="44" r="5.5" fill="{MOON}"/></g>
<g class="moth"><circle cx="64" cy="30" r="2" fill="{LAV}" opacity="0.8"/></g>
{watcher(186,158,1.05,SIL2)}
<ellipse class="fogdrift" cx="130" cy="180" rx="120" ry="8" fill="{LAV}" opacity="0.10"/>
<rect y="178" width="260" height="12" fill="{INK}"/>
"""
write("streetlamp.svg", svg(260, 190, lamp_body, "Streetlamp",
    "A streetlamp that dips once every few seconds, a moth circling its head, and a watcher standing at the edge of the light whose head turns and whose red eyes open briefly.", lamp_style))

# ------------------------------------------------------------ watcher eyes --
eyes_style = f"""
@keyframes slowblink{{0%,42%,58%,100%{{transform:scaleY(1)}}48%,53%{{transform:scaleY(0.06)}}}} .eye2{{transform-box:fill-box;transform-origin:center;animation:slowblink 7s {SINE} infinite}}
@keyframes track{{0%,24%{{transform:translate(-5px,0)}}40%,60%{{transform:translate(5px,0)}}76%,100%{{transform:translate(-5px,0)}}}} .track{{animation:track 7s {SINE} infinite}}
@keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}} .ring{{transform-origin:100px 100px;animation:spin 34s linear infinite}}
"""
eyes_body = f"""
<circle cx="100" cy="100" r="97" fill="{INK}"/>
<circle class="ring" cx="100" cy="100" r="90" fill="none" stroke="{SIL2}" stroke-width="2" stroke-dasharray="8 16"/>
<path d="M48 78 L94 88 M152 78 L106 88" stroke="#46587a" stroke-width="5" stroke-linecap="round"/>
<g class="eye2"><path d="M52 92 L92 99 L89 110 L55 104 Z" fill="{CREAM}" opacity="0.94"/>
<path d="M148 92 L108 99 L111 110 L145 104 Z" fill="{CREAM}" opacity="0.94"/>
<g class="track"><circle cx="72" cy="100" r="5.6" fill="{INK}"/><circle cx="128" cy="100" r="5.6" fill="{INK}"/>
<circle cx="72" cy="100" r="2" fill="{RED}"/><circle cx="128" cy="100" r="2" fill="{RED}"/></g></g>
<path d="M70 148 Q 100 140 130 148" stroke="{SIL2}" stroke-width="2.4" fill="none" opacity="0.7"/>
"""
write("watcher-eyes.svg", svg(200, 200, eyes_body, "Watcher eyes",
    "One pair of sharp, slanted eyes in the dark. The pupils track slowly side to side, and the blink is slow and heavy, with a red glint in each pupil.", eyes_style))

# ----------------------------------------------------------- glitch divider --
divider_style = f"""
@keyframes slice1{{0%,64%,72%,100%{{transform:translate(0,0);opacity:.9}}66%,70%{{transform:translate(-7px,-3px);opacity:1}}}} .slice1{{animation:slice1 6s linear infinite}}
@keyframes slice2{{0%,38%,46%,100%{{transform:translate(0,0);opacity:.9}}40%,44%{{transform:translate(9px,3px);opacity:1}}}} .slice2{{animation:slice2 6s linear infinite}}
@keyframes headtilt{{0%,30%,58%,100%{{transform:rotate(0deg)}}38%,50%{{transform:rotate(-11deg)}}}} .headtilt{{transform-box:fill-box;transform-origin:85% 85%;animation:headtilt 6.5s {SINE} infinite}}
@keyframes tailflick{{0%,71%,100%{{transform:rotate(0deg)}}76%{{transform:rotate(7deg)}}82%{{transform:rotate(-4deg)}}88%{{transform:rotate(0deg)}}}} .tailflick{{transform-box:fill-box;transform-origin:0 50%;animation:tailflick 6.5s {SHARP} infinite}}
@keyframes eyepulse{{0%,88%,100%{{opacity:.25}}92%,96%{{opacity:1}}}} .eyepulse{{animation:eyepulse 6.5s linear infinite}}
"""
divider_body = f"""
<line x1="8" y1="38" x2="330" y2="38" stroke="{GOLD}" stroke-width="1.6" opacity="0.7"/>
<line x1="392" y1="38" x2="712" y2="38" stroke="{GOLD}" stroke-width="1.6" opacity="0.7"/>
<rect class="slice1" x="120" y="36.6" width="52" height="2.8" fill="{RED}" opacity="0.9"/>
<rect class="slice2" x="548" y="36.6" width="52" height="2.8" fill="{LAV}" opacity="0.9"/>
<g transform="translate(361 34)">
<path d="M-7 -2 L-7 4 M5 -2 L5 4" stroke="{SIL2}" stroke-width="2"/>
<g class="tailflick"><path d="M17 -6 L46 3 L19 3 Z" fill="{SIL2}"/></g>
<path d="M-27 -1 Q-29 -17 -11 -20 Q7 -23 17 -13 Q24 -6 20 -1 Z" fill="{SIL2}"/>
<g class="headtilt"><circle cx="-21" cy="-17" r="8.5" fill="{SIL2}"/>
<path d="M-29 -17 L-40 -13.5 L-29 -11 Z" fill="{SIL2}"/>
<circle class="eyepulse" cx="-23.5" cy="-18.5" r="1.7" fill="{RED}"/></g></g>
"""
write("glitch-divider.svg", svg(720, 64, divider_body, "Glitch divider",
    "A divider line with brief glitch slices and a crow perched in the middle: it tilts its head, flicks its tail, and its red eye brightens for a moment.", divider_style))

# -------------------------------------------------------------- shadow walk --
walk_style = TWINKLE + WALK_CSS + f"""
@keyframes walkman{{0%{{transform:translateX(-46px)}}100%{{transform:translateX(716px)}}}} .walkman{{animation:walkman 9s {SMOOTH} infinite}}
@keyframes walkshadow{{0%{{transform:translateX(-88px)}}100%{{transform:translateX(668px)}}}} .walkshadow{{animation:walkshadow 9s {SMOOTH} infinite}}
"""
walk_body = f"""
<line x1="6" y1="86" x2="714" y2="86" stroke="{LAV}" stroke-width="2.2" stroke-dasharray="2 10" stroke-linecap="round" opacity="0.55"/>
{stars([(140,12,1.4),(420,8,1.2),(640,16,1.4)])}
<g transform="translate(0 88)"><g class="walkshadow" opacity="0.32"><g transform="scale(1 -0.5) skewX(-14)">{stickman(INK,1.0)}</g></g></g>
<g class="walkman"><g transform="translate(0 62)"><g class="bobw">{stickman(SIL2,1.0)}</g></g></g>
"""
write("shadow-walk.svg", svg(720, 96, walk_body, "Shadow walk",
    "A stickman walks across, and his flattened shadow walks with him but out of sync, a half-step behind and never quite matching his stride.", walk_style))

# -------------------------------------------------------------- the watcher --
watcher_style = TWINKLE + FLAP + WATCH + f"""
@keyframes fogdrift2{{0%{{transform:translateX(-20px)}}100%{{transform:translateX(20px)}}}} .fogdrift2{{animation:fogdrift2 12s {SINE} infinite alternate}}
@keyframes crowlate{{0%{{transform:translate(-120px,4px)}}30%{{transform:translate(180px,-6px)}}55%,100%{{transform:translate(860px,-2px)}}}} .crowlate{{animation:crowlate 22s {SINE} infinite}}
"""
watcher_body = f"""
{stars([(80,16,1.5),(210,26,1.2),(520,12,1.4),(668,22,1.2)])}
<circle cx="636" cy="30" r="14" fill="{MOON}" opacity="0.9"/><circle cx="630" cy="25" r="2.8" fill="#d9c globalization894"/>
<g class="crowlate">{crow(0,44,0.7,SIL2)}</g>
<path d="M0 110 L0 84 Q 200 66 360 78 T 720 82 L720 110 Z" fill="{SIL2}"/>
<path d="M0 110 L0 96 Q 240 84 470 92 T 720 94 L720 110 Z" fill="{SIL}"/>
{watcher(360,58,1.18,SIL)}
<ellipse class="fogdrift2" cx="360" cy="102" rx="230" ry="7" fill="{LAV}" opacity="0.10"/>
"""
watcher_body = watcher_body.replace("#d9c globalization894", "#d9c894")
write("the-watcher.svg", svg(720, 110, watcher_body, "The watcher",
    "A lone figure stands motionless on a hill in fog. After a long stillness its head turns toward you and two red eyes open, hold, and close again.", watcher_style))

# -------------------------------------------------------------------- raven --
raven_style = f"""
@keyframes lookr{{0%,26%,62%,100%{{transform:rotate(0deg)}}34%,54%{{transform:rotate(13deg)}}}} .lookr{{transform-box:fill-box;transform-origin:80% 85%;animation:lookr 8s {SINE} infinite}}
@keyframes tailf2{{0%,80%,100%{{transform:rotate(0deg)}}85%{{transform:rotate(6deg)}}91%{{transform:rotate(-3deg)}}}} .tailf2{{transform-box:fill-box;transform-origin:0 50%;animation:tailf2 8s {SHARP} infinite}}
@keyframes ruffle{{0%,100%{{transform:scale(1,1)}}50%{{transform:scale(1.02,1.035)}}}} .ruffle{{transform-box:fill-box;transform-origin:bottom center;animation:ruffle 4.6s {SINE} infinite}}
@keyframes eyepulse2{{0%,91%,100%{{opacity:.2}}94%,97%{{opacity:1}}}} .eyepulse2{{animation:eyepulse2 9s linear infinite}}
@keyframes eyepulse3{{0%,78%,100%{{opacity:.15}}82%,86%{{opacity:.9}}}} .eyepulse3{{animation:eyepulse3 11s linear infinite}}
"""
def small_crow(x, y, eye_cls, delay):
    return (f'<g transform="translate({x} {y})"><path d="M-16 0 Q-17 -11 -6 -13 Q5 -15 10 -8 Q14 -3 11 0 Z" fill="{SIL2}"/>'
            f'<path d="M10 -4 L24 2 L11 2 Z" fill="{SIL2}"/><circle cx="-9" cy="-9" r="5.5" fill="{SIL2}"/>'
            f'<path d="M-14 -9 L-21 -6.5 L-14 -5 Z" fill="{SIL2}"/>'
            f'<circle class="{eye_cls}" style="animation-delay:{delay}s" cx="-10.5" cy="-10" r="1.2" fill="{RED}"/></g>')
raven_body = f"""
<path d="M4 40 Q 200 30 380 38 T 716 34" stroke="#3a4034" stroke-width="3" fill="none"/>
<g transform="translate(300 36)"><g class="ruffle">
<path d="M-8 -4 L-8 3 M6 -4 L6 3" stroke="{SIL2}" stroke-width="2.2"/>
<g class="tailf2"><path d="M20 -6 L44 6 L21 2 Z" fill="{SIL2}"/></g>
<path d="M-30 -2 Q-33 -22 -12 -27 Q8 -30 19 -16 Q26 -7 21 -1 Z" fill="{SIL2}"/>
<g class="lookr"><circle cx="-24" cy="-20" r="10" fill="{SIL2}"/>
<path d="M-33 -20 L-47 -15.5 L-33 -12.5 Z" fill="{SIL2}"/>
<circle cx="-27" cy="-22" r="1.9" fill="{RED}" opacity="0.85"/></g></g></g>
{small_crow(566,38,"eyepulse2",0)}
{small_crow(636,37,"eyepulse3",0)}
"""
write("raven.svg", svg(720, 64, raven_body, "Raven",
    "A raven perched on a branch slowly turns its head to look, flicks its tail, and ruffles; two smaller crows sit further along, their red eyes brightening now and then.", raven_style))

# ------------------------------------------------------------------ rooftop --
roof_style = TWINKLE + FLAP + f"""
@keyframes winflick{{0%,100%{{opacity:.75}}42%{{opacity:.3}}48%{{opacity:.8}}70%{{opacity:.45}}76%{{opacity:.75}}}} .winflick{{animation:winflick 6.4s linear infinite}}
@keyframes flutter{{0%,100%{{transform:rotate(-3deg)}}50%{{transform:rotate(4deg)}}}} .flutter{{transform-box:fill-box;transform-origin:top center;animation:flutter 3.4s {SINE} infinite}}
@keyframes fogmove3{{0%{{transform:translateX(-36px)}}100%{{transform:translateX(36px)}}}} .fogmove3{{animation:fogmove3 16s {SINE} infinite alternate}}
@keyframes crowroof{{0%{{transform:translate(-130px,2px)}}40%{{transform:translate(330px,-8px)}}100%{{transform:translate(1010px,0)}}}} .crowroof{{animation:crowroof 26s {SINE} infinite}}
"""
def win(x, y, delay):
    return f'<rect class="winflick" style="animation-delay:{delay}s" x="{x}" y="{y}" width="7" height="10" fill="{GOLD}"/>'
roof_body = f"""
<circle cx="806" cy="24" r="14" fill="{MOON}"/><circle cx="800" cy="19" r="2.8" fill="#d9c894"/>
{stars([(120,16,1.5),(300,24,1.2),(520,12,1.4),(660,26,1.1)])}
<g class="crowroof">{crow(0,30,0.72,SIL)}</g>
<g fill="{SIL}">
<rect x="30" y="66" width="86" height="74"/><rect x="140" y="48" width="70" height="92"/>
<rect x="232" y="78" width="96" height="62"/><rect x="352" y="38" width="76" height="102"/>
<rect x="452" y="62" width="92" height="78"/><rect x="568" y="44" width="68" height="96"/>
<rect x="660" y="74" width="88" height="66"/><rect x="770" y="56" width="80" height="84"/>
</g>
{win(52,84,-1.2)}{win(168,66,-3.4)}{win(258,94,-2.1)}{win(376,58,-4.6)}{win(480,82,-0.7)}{win(592,62,-2.9)}{win(688,92,-5.2)}{win(796,74,-1.8)}{win(86,106,-4.1)}{win(492,108,-3.0)}
<g transform="translate(390 38)"><g class="flutter"><path d="M-3 -24 L9 -24 L13 0 L-6 0 Z" fill="{INK}"/></g>
<g stroke="{INK}" stroke-width="3.2" stroke-linecap="round"><line x1="0" y1="-24" x2="0" y2="-2"/><line x1="0" y1="-2" x2="-7" y2="0"/><line x1="0" y1="-2" x2="7" y2="0"/></g>
<circle cx="0" cy="-31" r="7" fill="{INK}"/></g>
<ellipse class="fogmove3" cx="300" cy="132" rx="200" ry="8" fill="{LAV}" opacity="0.10"/>
<ellipse class="fogmove3" style="animation-duration:22s" cx="640" cy="126" rx="170" ry="7" fill="{LAV}" opacity="0.08"/>
"""
write("rooftop.svg", svg(880, 140, roof_body, "Rooftop watcher",
    "A night skyline with a few flickering windows. A lone figure stands on the tallest roof, coat fluttering, watching the city while fog drifts below and a crow crosses the moon.", roof_style))

# --------------------------------------------------------------------- mist --
mist_style = f"""
@keyframes drift1{{from{{transform:translateX(0)}}to{{transform:translateX(-360px)}}}} .d1{{animation:drift1 34s {SINE} infinite}}
@keyframes drift2{{from{{transform:translateX(-360px)}}to{{transform:translateX(0)}}}} .d2{{animation:drift2 46s {SINE} infinite}}
@keyframes farwalk{{0%{{transform:translateX(-40px)}}100%{{transform:translateX(760px)}}}} .farwalk{{animation:farwalk 30s {SINE} infinite}}
""" + WALK_CSS
mist_path = lambda y, fill, op: (f'<path d="M0 {y} Q 90 {y-16} 180 {y} T 360 {y} T 540 {y} T 720 {y} T 900 {y} T 1080 {y} L1080 84 L0 84 Z" fill="{fill}" opacity="{op}"/>')
mist_body = f"""
<g class="d1">{mist_path(34, LAV, 0.26)}</g>
<g class="farwalk" opacity="0.55"><g transform="translate(0 44)">{stickman(INK,0.8)}</g></g>
<g class="d2">{mist_path(54, SAGE, 0.3)}</g>
<g class="d1" style="animation-duration:52s">{mist_path(72, GOLD, 0.24)}</g>
"""
write("mist.svg", svg(720, 84, mist_body, "Mist",
    "Slow layers of mist drift against each other, and far behind them a small dark figure walks through, half hidden, never hurrying.", mist_style))

print("done")
