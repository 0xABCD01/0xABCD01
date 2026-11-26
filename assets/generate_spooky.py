#!/usr/bin/env python3
"""Spooky-cute SVG set for the 0xABCD01 profile README.

Theme picked from research (2026-11-26): haunted-house CSS art (flickering
windows, floating ghost, bats across a full moon), cute floating ghosts,
dangling spiders, jack-o'-lantern candle flicker, blinking eyes in the dark,
and the Pac-Man ghost-chase idea (the contribution graph itself is switched
from snake to Pac-Man in .github/workflows/haunted.yml).

Motion is CSS inside the SVG only (GitHub renders these via <img>, no JS).
Palette keeps the old navy/cream/lavender/sage/gold identity and adds
pumpkin orange as the spooky accent.
"""
import os

ASSETS = os.path.dirname(os.path.abspath(__file__))

NAVY = "#16213a"; NAVY2 = "#1f2c4d"; DARK = "#0d1526"
CREAM = "#f8f1e6"; MOON = "#f6e3b4"; LAV = "#c9c3d9"; SAGE = "#a9b9a4"
GOLD = "#c3a36a"; ORANGE = "#e07b39"; ORANGE_L = "#f2a65a"; GHOST = "#f4efe4"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

def svg(w, h, body, title, desc, style):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{style}</style>{body}</svg>\n')

def write(name, content):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(content)
    print("wrote", name, len(content))

def bat(x, y, s, fill=DARK):
    return (f'<path d="M{x} {y} q{6*s} {-7*s} {12*s} 0 q{3*s} {-5*s} {6*s} {-5*s} '
            f'q{3*s} 0 {6*s} {5*s} q{6*s} {-7*s} {12*s} 0 q{-6*s} {9*s} {-12*s} {3*s} '
            f'q{-3*s} {-2*s} {-6*s} {-3*s} q{-3*s} {1*s} {-6*s} {3*s} q{-6*s} {-6*s} {-12*s} {-3*s} Z" fill="{fill}"/>')

def ghost(x, y, s, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c} transform="translate({x} {y}) scale({s})">'
            f'<path d="M0 -26 C -16 -26 -22 -12 -22 2 L -22 26 L -15 19 L -8 26 L 0 19 L 8 26 L 15 19 L 22 26 L 22 2 C 22 -12 16 -26 0 -26 Z" fill="{GHOST}"/>'
            f'<circle cx="-8" cy="-4" r="3.2" fill="{NAVY}"/><circle cx="8" cy="-4" r="3.2" fill="{NAVY}"/>'
            f'<ellipse cx="0" cy="5" rx="4" ry="5.5" fill="{NAVY}"/>'
            f'<circle cx="-14" cy="3" r="3.4" fill="{ORANGE_L}" opacity="0.55"/><circle cx="14" cy="3" r="3.4" fill="{ORANGE_L}" opacity="0.55"/></g>')

def stars(points, cls="tw"):
    out = ""
    for i, (x, y, r) in enumerate(points):
        out += f'<circle class="{cls}" style="animation-delay:{i*0.7:.1f}s" cx="{x}" cy="{y}" r="{r}" fill="{CREAM}"/>'
    return out

TWINKLE = "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.4s ease-in-out infinite}"

# ------------------------------------------------------------------ banner --
banner_style = """
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.4s ease-in-out infinite}
@keyframes moonglow{0%,100%{opacity:.35}50%{opacity:.7}} .mg{animation:moonglow 5s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-13px)}} .bob{animation:bob 3.6s ease-in-out infinite}
@keyframes fly1{0%{transform:translate(-180px,0)}100%{transform:translate(1780px,-46px)}} .fly1{animation:fly1 17s linear infinite}
@keyframes fly2{0%{transform:translate(-140px,0)}100%{transform:translate(1740px,30px)}} .fly2{animation:fly2 23s linear infinite;animation-delay:-9s}
@keyframes flick{0%,100%{opacity:1}8%{opacity:.25}12%{opacity:1}46%{opacity:1}50%{opacity:.35}54%{opacity:1}78%{opacity:.5}82%{opacity:1}} .fl{animation:flick 4.2s linear infinite}
@keyframes flick2{0%,100%{opacity:.9}30%{opacity:.2}36%{opacity:.95}64%{opacity:.4}70%{opacity:.9}} .fl2{animation:flick2 5.1s linear infinite}
@keyframes flash{0%,60%,66%,100%{opacity:0}62%,64%{opacity:.55}} .flash{animation:flash 9s linear infinite}
@keyframes bolt{0%,60%,66%,100%{opacity:0}62%,64%{opacity:.95}} .bolt{animation:bolt 9s linear infinite}
@keyframes typeout{0%{transform:scaleX(0)}55%,100%{transform:scaleX(1)}} .ty{transform-origin:88px 0;animation:typeout 7s steps(26) infinite}
@keyframes sway{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}} .sway{transform-origin:top center;animation:sway 4.5s ease-in-out infinite}
"""
house = f"""
<g>
  <path d="M1150 420 L1150 250 L1235 190 L1320 250 L1320 420 Z" fill="{DARK}"/>
  <path d="M1128 252 L1235 176 L1342 252 L1328 252 L1235 188 L1142 252 Z" fill="{NAVY2}"/>
  <rect x="1218" y="150" width="34" height="52" fill="{DARK}"/>
  <path d="M1210 152 L1235 128 L1260 152 Z" fill="{NAVY2}"/>
  <rect class="fl" x="1227" y="162" width="16" height="20" rx="8" fill="{ORANGE_L}"/>
  <rect class="fl2" x="1172" y="282" width="26" height="34" rx="3" fill="{ORANGE}"/>
  <rect class="fl" style="animation-delay:-2s" x="1272" y="282" width="26" height="34" rx="3" fill="{ORANGE_L}"/>
  <rect x="1222" y="330" width="26" height="90" rx="12" fill="{NAVY2}"/>
  <circle cx="1241" cy="378" r="2.6" fill="{GOLD}"/>
  <path d="M1150 420 L1320 420 L1360 420 L1105 420 Z" fill="{DARK}"/>
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
<g class="bob">{ghost(1062,318,1.25)}</g>
<g class="sway">{bat(300,352,0.9,DARK)}</g>
<text x="88" y="196" font-family="{MONO}" font-size="96" font-weight="700" fill="{CREAM}">0xABCD01</text>
<text x="92" y="252" font-family="{MONO}" font-size="27" letter-spacing="6" fill="{GOLD}">BUG BOUNTY · PENTEST · OSINT</text>
<g><clipPath id="tc"><rect class="ty" x="88" y="286" width="560" height="40"/></clipPath>
<text clip-path="url(#tc)" x="90" y="318" font-family="{MONO}" font-size="26" fill="{SAGE}">$ boo. found your bug_</text></g>
<circle cx="118" cy="368" r="4" fill="{ORANGE}"/><circle cx="170" cy="360" r="3" fill="{LAV}"/><circle cx="228" cy="370" r="3.4" fill="{GOLD}"/>
<path d="M118 368 L170 360 L228 370" stroke="{LAV}" stroke-width="1.3" opacity="0.55" fill="none"/>
"""
write("haunted-banner.svg", svg(1600, 420, banner_body, "0xABCD01 haunted banner",
    "A haunted night banner: a glowing full moon, bats, a flickering haunted house, a cute floating ghost, and a lightning flash, over the handle 0xABCD01.", banner_style))

# ------------------------------------------------------------ haunted house --
hh_style = """
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.4s ease-in-out infinite}
@keyframes peek{0%,18%{transform:translateY(26px);opacity:0}30%,62%{transform:translateY(0);opacity:1}76%,100%{transform:translateY(26px);opacity:0}} .peek{animation:peek 7s ease-in-out infinite}
@keyframes dangle{0%,100%{transform:translateY(0)}50%{transform:translateY(30px)}} .dangle{animation:dangle 6s ease-in-out infinite}
@keyframes flick{0%,100%{opacity:1}10%{opacity:.25}14%{opacity:1}52%{opacity:.35}58%{opacity:1}} .fl{animation:flick 4.4s linear infinite}
@keyframes flyh{0%{transform:translate(-40px,0)}100%{transform:translate(300px,-14px)}} .flyh{animation:flyh 11s linear infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}} .bob{animation:bob 3.6s ease-in-out infinite}
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
<g clip-path="url(#attic)"><g class="peek">{ghost(130,38,0.34)}</g></g>
<rect class="fl" x="70" y="112" width="22" height="28" rx="3" fill="{ORANGE_L}"/>
<rect class="fl" style="animation-delay:-2.2s" x="168" y="112" width="22" height="28" rx="3" fill="{ORANGE}"/>
<rect x="119" y="128" width="22" height="50" rx="10" fill="{NAVY2}"/><circle cx="135" cy="154" r="2" fill="{GOLD}"/>
<g class="dangle"><line x1="206" y1="86" x2="206" y2="112" stroke="{LAV}" stroke-width="1.2"/>
<g transform="translate(206 120)"><circle r="6.5" fill="{DARK}" stroke="{LAV}" stroke-width="1"/>
<path d="M-5 -3 L-13 -8 M-6 0 L-14 0 M-5 3 L-12 8 M5 -3 L13 -8 M6 0 L14 0 M5 3 L12 8" stroke="{LAV}" stroke-width="1.3" fill="none"/>
<circle cx="-2" cy="-1.6" r="1.1" fill="{ORANGE_L}"/><circle cx="2" cy="-1.6" r="1.1" fill="{ORANGE_L}"/></g></g>
<g class="bob">{ghost(34,158,0.55)}</g>
<rect y="178" width="260" height="12" fill="{DARK}"/>
"""
write("haunted-house.svg", svg(260, 190, hh_body, "Haunted house",
    "A small haunted house: a ghost peeks from the attic window, a spider dangles from the roof, windows flicker, and a bat crosses the moon.", hh_style))

# -------------------------------------------------------------- spooky eyes --
eyes_style = """
@keyframes blink{0%,91%,100%{transform:scaleY(1)}94%{transform:scaleY(0.08)}97%{transform:scaleY(1)}} .eye{transform-box:fill-box;transform-origin:center;animation:blink 4.6s ease-in-out infinite}
@keyframes look{0%,22%{transform:translateX(-4px)}38%,62%{transform:translateX(4px)}78%,100%{transform:translateX(-4px)}} .pupil{animation:look 5.2s ease-in-out infinite}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}} .ring{transform-origin:100px 100px;animation:spin 26s linear infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}} .bob{animation:bob 3.4s ease-in-out infinite}
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
{eye_pair(72,108,0.72,-1.6)}
{eye_pair(134,116,0.55,-3.1)}
<g class="bob">{ghost(100,164,0.62)}</g>
"""
write("spooky-eyes.svg", svg(200, 200, eyes_body, "Eyes in the dark",
    "Pairs of eyes blink in the dark and glance side to side while a small ghost bobs below them.", eyes_style))

# -------------------------------------------------------------- ghost chase --
chase_style = """
@keyframes run{0%{transform:translateX(-70px)}100%{transform:translateX(760px)}} .run{animation:run 7s linear infinite}
@keyframes rung{0%{transform:translateX(-170px)}100%{transform:translateX(660px)}} .rung{animation:rung 7s linear infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}} .bob{animation:bob 0.9s ease-in-out infinite}
@keyframes legw{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}} .leg{transform-box:fill-box;transform-origin:top center;animation:legw 0.36s ease-in-out infinite}
@keyframes boo{0%,72%{opacity:0;transform:scale(0.6)}80%,90%{opacity:1;transform:scale(1.08)}97%,100%{opacity:0;transform:scale(1)}} .boo{transform-origin:618px 26px;animation:boo 7s linear infinite}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3s ease-in-out infinite}
"""
bug = f"""<g class="run"><g transform="translate(0 58)">
<g class="leg"><path d="M-8 6 L-15 16 M0 8 L-1 18 M8 6 L14 16" stroke="{GOLD}" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>
<ellipse cx="0" cy="0" rx="17" ry="11" fill="{NAVY2}"/><ellipse cx="9" cy="-2" rx="8" ry="7" fill="{GOLD}"/>
<circle cx="12" cy="-4" r="1.8" fill="{DARK}"/>
<path d="M14 -8 Q 22 -16 26 -14 M12 -9 Q 17 -18 22 -18" stroke="{GOLD}" stroke-width="2" fill="none" stroke-linecap="round"/>
</g></g>"""
chase_body = f"""
<line x1="6" y1="72" x2="714" y2="72" stroke="{LAV}" stroke-width="2.4" stroke-dasharray="2 10" stroke-linecap="round" opacity="0.7"/>
{stars([(120,16,1.6),(330,10,1.4),(560,18,1.6)],)}
<g class="rung"><g class="bob">{ghost(0,52,0.95)}</g></g>
{bug}
<text class="boo" opacity="0" x="592" y="34" font-family="{MONO}" font-size="21" font-weight="700" fill="{ORANGE_L}">BOO!</text>
"""
write("ghost-chase.svg", svg(720, 96, chase_body, "Ghost chase",
    "A cute ghost chases a bug along a dotted path and shouts BOO! as it nearly catches it.", chase_style))

# ------------------------------------------------------------ spider divider --
spider_style = """
@keyframes drop{0%,16%{transform:translateY(0)}46%,62%{transform:translateY(26px)}88%,100%{transform:translateY(0)}} .drop{animation:drop 8s ease-in-out infinite}
@keyframes thread{0%,16%{transform:scaleY(1)}46%,62%{transform:scaleY(3.17)}88%,100%{transform:scaleY(1)}} .thread{transform-origin:360px 0;animation:thread 8s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.2s ease-in-out infinite}
"""
spider_body = f"""
<line x1="8" y1="34" x2="330" y2="34" stroke="{GOLD}" stroke-width="1.6" opacity="0.75"/>
<line x1="390" y1="34" x2="712" y2="34" stroke="{GOLD}" stroke-width="1.6" opacity="0.75"/>
<circle class="tw" cx="352" cy="34" r="2.6" fill="{LAV}"/><circle class="tw" style="animation-delay:-1.4s" cx="368" cy="34" r="2.6" fill="{LAV}"/>
<rect class="thread" x="359.4" y="0" width="1.4" height="12" fill="{LAV}"/>
<g class="drop"><g transform="translate(360 12)">
<path d="M-5 -3 L-14 -9 M-6 0 L-15 0 M-5 3 L-13 9 M5 -3 L14 -9 M6 0 L15 0 M5 3 L13 9" stroke="{CREAM}" stroke-width="1.5" fill="none"/>
<circle r="7.5" fill="{NAVY2}" stroke="{CREAM}" stroke-width="1.2"/>
<circle cx="-2.4" cy="-1.8" r="1.3" fill="{ORANGE_L}"/><circle cx="2.4" cy="-1.8" r="1.3" fill="{ORANGE_L}"/>
<path d="M-3 3.4 Q 0 5.4 3 3.4" stroke="{ORANGE_L}" stroke-width="1.2" fill="none"/></g></g>
"""
write("spider-divider.svg", svg(720, 64, spider_body, "Spider divider",
    "A divider line with a spider that drops down on its thread, grins, and climbs back up.", spider_style))

# ------------------------------------------------------------ pumpkin pulse --
pump_style = """
@keyframes candle{0%,100%{opacity:1}22%{opacity:.45}30%{opacity:1}58%{opacity:.6}66%{opacity:1}84%{opacity:.5}92%{opacity:1}} .candle{animation:candle 3.8s linear infinite}
@keyframes swapA{0%,44%{opacity:1}52%,92%{opacity:0}100%{opacity:1}} .swapA{animation:swapA 7s linear infinite}
@keyframes swapB{0%,44%{opacity:0}52%,92%{opacity:1}100%{opacity:0}} .swapB{animation:swapB 7s linear infinite}
@keyframes swayp{0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}} .swayp{transform-box:fill-box;transform-origin:bottom center;animation:swayp 5s ease-in-out infinite}
"""
def pumpkin(cx, face_cls="candle", extra=""):
    return (f'<g class="swayp"><g transform="translate({cx} 34)">'
            f'<path d="M-2 -24 Q 0 -30 5 -31" stroke="{SAGE}" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="27" ry="21" fill="{ORANGE}"/>'
            f'<ellipse cx="0" cy="0" rx="14" ry="20" fill="none" stroke="#c96a2e" stroke-width="2"/>'
            f'<ellipse cx="0" cy="0" rx="25" ry="20" fill="none" stroke="#c96a2e" stroke-width="2"/>'
            f'{extra}</g></g>')
face_cute = f'<g class="candle"><path d="M-13 -6 L-7 -13 L-1 -6 Z M13 -6 L7 -13 L1 -6 Z" fill="{MOON}"/><path d="M-13 6 L-8 11 L-3 6 L2 11 L7 6 L12 11 L10 3 L-11 3 Z" fill="{MOON}"/></g>'
face_scary = f'<g class="candle"><path d="M-14 -5 L-6 -12 L-2 -4 Z M14 -5 L6 -12 L2 -4 Z" fill="{DARK}"/><path d="M-12 8 L-7 2 L-2 8 L3 2 L8 8 L12 3 L11 10 L-11 10 Z" fill="{DARK}"/></g>'
mid_faces = f'<g class="swapA">{face_cute}</g><g class="swapB">{face_scary}</g>'
pump_body = f"""
<path d="M4 40 Q 90 26 180 38 T 360 38 T 540 38 T 716 36" stroke="{SAGE}" stroke-width="2.2" fill="none" opacity="0.8"/>
{pumpkin(180, extra=face_cute)}
{pumpkin(360, extra=mid_faces)}
{pumpkin(540, extra=face_cute)}
"""
write("pumpkin-pulse.svg", svg(720, 64, pump_body, "Pumpkin row",
    "Three jack-o'-lanterns on a vine; their candle faces flicker, and the middle one keeps swapping between a grin and a scary face.", pump_style))

# ---------------------------------------------------------------- graveyard --
grave_style = """
@keyframes rise{0%,14%{transform:translateY(24px);opacity:0}30%,58%{transform:translateY(0);opacity:1}76%,100%{transform:translateY(24px);opacity:0}} .rise{animation:rise 10s ease-in-out infinite}
@keyframes fogmove{0%{transform:translateX(-46px)}100%{transform:translateX(46px)}} .fogm{animation:fogmove 9s ease-in-out infinite alternate}
@keyframes fogmove2{0%{transform:translateX(38px)}100%{transform:translateX(-38px)}} .fogm2{animation:fogmove2 12s ease-in-out infinite alternate}
@keyframes blink{0%,90%,100%{opacity:1}94%{opacity:0}} .blink{animation:blink 5.4s linear infinite}
@keyframes hang{0%,100%{transform:rotate(5deg)}50%{transform:rotate(-5deg)}} .hang{transform-origin:118px 26px;animation:hang 4.2s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}} .tw{animation:tw 3.6s ease-in-out infinite}
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
<g class="blink"><circle cx="300" cy="98" r="2.6" fill="{ORANGE_L}"/><circle cx="312" cy="98" r="2.6" fill="{ORANGE_L}"/></g>
<g class="blink" style="animation-delay:-2.6s"><circle cx="566" cy="104" r="2.3" fill="{ORANGE_L}"/><circle cx="577" cy="104" r="2.3" fill="{ORANGE_L}"/></g>
<g class="fogm"><ellipse cx="240" cy="122" rx="150" ry="10" fill="{LAV}" opacity="0.16"/><ellipse cx="620" cy="128" rx="170" ry="9" fill="{LAV}" opacity="0.13"/></g>
<g class="fogm2"><ellipse cx="440" cy="118" rx="130" ry="8" fill="{CREAM}" opacity="0.10"/></g>
"""
write("graveyard.svg", svg(880, 140, grave_body, "Graveyard",
    "A graveyard at night: a ghost rises from behind a tombstone marked BUGS, fog drifts, eyes blink in the dark, and a bat hangs upside down from a dead tree.", grave_style))

# ---------------------------------------------------------------------- fog --
fog_style = """
@keyframes drift1{from{transform:translateX(0)}to{transform:translateX(-360px)}} .d1{animation:drift1 15s linear infinite}
@keyframes drift2{from{transform:translateX(-360px)}to{transform:translateX(0)}} .d2{animation:drift2 21s linear infinite}
@keyframes pass{0%{transform:translate(-70px,0)}100%{transform:translate(790px,-6px)}} .pass{animation:pass 16s linear infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}} .bob{animation:bob 2.8s ease-in-out infinite}
@keyframes blink{0%,89%,100%{opacity:1}93%{opacity:0}} .blink{animation:blink 4.8s linear infinite}
"""
mist = lambda y, fill, op: (f'<path d="M0 {y} Q 90 {y-16} 180 {y} T 360 {y} T 540 {y} T 720 {y} T 900 {y} T 1080 {y} L1080 84 L0 84 Z" fill="{fill}" opacity="{op}"/>')
fog_body = f"""
<g class="pass"><g class="bob">{ghost(0,34,0.72)}</g></g>
<g class="blink"><circle cx="520" cy="52" r="2.5" fill="{ORANGE_L}"/><circle cx="532" cy="52" r="2.5" fill="{ORANGE_L}"/></g>
<g class="d1">{mist(38, LAV, 0.35)}</g>
<g class="d2">{mist(56, SAGE, 0.4)}</g>
<g class="d1" style="animation-duration:24s">{mist(72, GOLD, 0.35)}</g>
"""
write("fog.svg", svg(720, 84, fog_body, "Rolling fog",
    "Layers of fog drift past each other while a small ghost glides through and a pair of eyes blinks from the mist.", fog_style))

print("done")
