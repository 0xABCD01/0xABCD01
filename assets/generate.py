#!/usr/bin/env python3
"""Generate SVG decorations for the 0xABCD01 profile README.

Visual language: a constellation graph. Nodes are targets, links are the
connections between them. Palette is inherited from the original banner
(navy / cream / lavender / sage / gold) so the whole profile reads as one
system.

Motion: everything animates with CSS inside the SVG, because GitHub renders
these through an <img> tag where scripts never run. Only transform, opacity,
and the SVG geometry properties are animated, so the motion stays cheap.

  - a pulse travels the links, as if a trace were running
  - a small bug walks the graph, hopping from node to node
  - a terminal line types itself under the handle
  - the divider sends a pulse outward from its centre
  - nodes and sparkles twinkle on staggered offsets
"""

import os

ASSETS = "/tmp/opencode/profrepo/assets"

NAVY_1 = "#18253d"
NAVY_2 = "#24262b"
CREAM = "#f8f1e6"
LAV = "#c9c3d9"
SAGE = "#a9b9a4"
GOLD = "#c3a36a"
GOLD_D = "#b8935a"  # darker gold, stays legible on a light background

MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

# The graph the bug walks. Straight segments between nodes.
# The terminal line lives in the bottom-left corner, well below the lowest
# node, so the bug never walks through the text.
WALK = [(106, 332), (246, 266), (306, 178), (626, 176), (909, 151), (1090, 92)]
WALK_D = "M" + " L".join(f"{x} {y}" for x, y in WALK)


def sparkle(x, y, s=1.0, fill=LAV, op=0.85, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (
        f'<path{c} d="M {x} {y - 6 * s} C {x} {y - 2 * s} {x + 2 * s} {y} {x + 6 * s} {y} '
        f'C {x + 2 * s} {y} {x} {y + 2 * s} {x} {y + 6 * s} '
        f'C {x} {y + 2 * s} {x - 2 * s} {y} {x - 6 * s} {y} '
        f'C {x - 2 * s} {y} {x} {y - 2 * s} {x} {y - 6 * s} Z" '
        f'fill="{fill}" opacity="{op}"/>'
    )


def node(x, y, r, fill, op=1.0, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<circle{c} cx="{x}" cy="{y}" r="{r}" fill="{fill}" opacity="{op}"/>'


def link(x1, y1, x2, y2, stroke, w=1.4, op=0.6):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>'
    )


def svg(w, h, body, title=None, desc=None):
    t = f"<title>{title}</title>" if title else ""
    d = f"<desc>{desc}</desc>" if desc else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d">{t}{d}{body}</svg>\n'
    )


# ---------------------------------------------------------------- banner ----

BANNER_CSS = """
  @keyframes trace {
    0%   { stroke-dashoffset: 0;    opacity: 0; }
    6%   { opacity: 0.9; }
    88%  { opacity: 0.9; }
    100% { stroke-dashoffset: -1056; opacity: 0; }
  }
  @keyframes twinkle {
    0%, 100% { opacity: 0.32; }
    50%      { opacity: 1; }
  }
  @keyframes bugmove {
    0%    { translate: 106px 332px; rotate: -25.2deg; opacity: 0; }
    2%    { translate: 106px 332px; rotate: -25.2deg; opacity: 1; }
    14.7% { translate: 246px 266px; rotate: -25.2deg; opacity: 1; }
    15.5% { translate: 246px 266px; rotate: -55.7deg; opacity: 1; }
    24.8% { translate: 306px 178px; rotate: -55.7deg; opacity: 1; }
    25.6% { translate: 306px 178px; rotate: -0.4deg;  opacity: 1; }
    55.1% { translate: 626px 176px; rotate: -0.4deg;  opacity: 1; }
    55.9% { translate: 626px 176px; rotate: -5deg;    opacity: 1; }
    82%   { translate: 909px 151px; rotate: -5deg;    opacity: 1; }
    82.8% { translate: 909px 151px; rotate: -18.1deg; opacity: 1; }
    97%   { translate: 1090px 92px; rotate: -18.1deg; opacity: 1; }
    100%  { translate: 1090px 92px; rotate: -18.1deg; opacity: 0; }
  }
  @keyframes bughop {
    0%, 13%   { translate: 0 0px;   scale: 1 1; }
    7%         { translate: 0 -5px;  scale: 1 1; }
    14.7%, 17%{ translate: 0 0px;   scale: 1.1 0.9; }
    20%        { translate: 0 -5px;  scale: 1 1; }
    24.8%, 27%{ translate: 0 0px;   scale: 1.1 0.9; }
    39%        { translate: 0 -5px;  scale: 1 1; }
    55.1%, 58%{ translate: 0 0px;   scale: 1.1 0.9; }
    69%        { translate: 0 -5px;  scale: 1 1; }
    82%, 85%  { translate: 0 0px;   scale: 1.1 0.9; }
    90%        { translate: 0 -5px;  scale: 1 1; }
    97%, 100% { translate: 0 0px;   scale: 1 1; }
  }
  @keyframes typeout {
    0%   { transform: scaleX(0); }
    60%  { transform: scaleX(1); }
    100% { transform: scaleX(1); }
  }
  @keyframes termfade {
    0%, 2%   { opacity: 0; }
    7%, 94%  { opacity: 1; }
    99%,100% { opacity: 0; }
  }
  @keyframes cursor {
    0%, 49%   { opacity: 1; }
    50%, 100% { opacity: 0; }
  }

  .trace { animation: trace 5.2s linear infinite; }
  .tw-a { animation: twinkle 4.4s ease-in-out infinite; }
  .tw-b { animation: twinkle 5.1s ease-in-out 0.9s infinite; }
  .tw-c { animation: twinkle 6.3s ease-in-out 1.7s infinite; }
  .tw-d { animation: twinkle 5.6s ease-in-out 2.4s infinite; }
  .tw-e { animation: twinkle 4.9s ease-in-out 3.1s infinite; }
  .tw-f { animation: twinkle 6.0s ease-in-out 0.4s infinite; }

  .bug-move {
    transform-box: view-box;
    transform-origin: 0 0;
    animation: bugmove 22s linear infinite;
  }
  .bug-hop {
    transform-box: fill-box;
    transform-origin: center;
    animation: bughop 22s linear infinite;
  }

  .typer-mask {
    transform-box: fill-box;
    transform-origin: 0% 50%;
    animation: typeout 9s steps(22, end) infinite;
  }
  .term-fade { animation: termfade 9s ease-in-out infinite; }
  .cursor { animation: cursor 1.05s steps(1, end) infinite; }
"""

BUG_BODY = f"""  <g class="bug-body">
    <path d="M-9.5 -3.4 L-9.5 3.4" stroke="{GOLD}" stroke-width="2" stroke-linecap="round" />
    <ellipse cx="-2.4" cy="0" rx="7.8" ry="8.8" fill="{GOLD}" />
    <ellipse cx="-4" cy="-1.8" rx="4.9" ry="6" fill="{CREAM}" opacity="0.22" />
    <circle cx="6.6" cy="0" r="4.9" fill="{GOLD}" />
    <path d="M9.8 -2.6 L15.2 -6.1 M9.8 2.6 L15.2 6.1" stroke="{GOLD}" stroke-width="1.8" stroke-linecap="round" />
    <path d="M-4.9 -7.4 L-9.8 -12 M-0.6 -8.8 L-2.3 -13.8 M0.9 -8.8 L3.2 -13.8" stroke="{GOLD}" stroke-width="1.7" stroke-linecap="round" />
    <path d="M-4.9 7.4 L-9.8 12 M-0.6 8.8 L-2.3 13.8 M0.9 8.8 L3.2 13.8" stroke="{GOLD}" stroke-width="1.7" stroke-linecap="round" />
    <circle cx="-2.4" cy="0" r="1.5" fill="{NAVY_1}" opacity="0.4" />
    <circle cx="8.1" cy="-1.6" r="1.3" fill="{NAVY_1}" />
  </g>"""


def banner():
    body = f"""  <style>{BANNER_CSS}  </style>
  <defs>
    <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NAVY_1}" />
      <stop offset="1" stop-color="{NAVY_2}" />
    </linearGradient>
    <linearGradient id="cream" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CREAM}" />
      <stop offset="1" stop-color="#e8e0d5" />
    </linearGradient>
    <pattern id="dots" width="34" height="34" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="{CREAM}" opacity="0.16" />
    </pattern>
    <clipPath id="typer">
      <rect class="typer-mask" x="99" y="373" width="226" height="24" />
    </clipPath>
  </defs>

  <rect width="1600" height="420" rx="28" fill="url(#wash)" />
  <rect x="930" y="0" width="670" height="420" fill="url(#dots)" opacity="0.5" />

  <!-- cave mouth -->
  <path d="M1010 420C1010 185 1160 48 1374 48c115 0 174 38 226 92v280z" fill="url(#cream)" opacity="0.96" />
  <path d="M1118 420c0-157 101-268 247-268 86 0 153 37 235 111v157z" fill="{LAV}" opacity="0.75" />
  <path d="M1244 420c0-94 63-166 147-166 79 0 147 62 209 143v23z" fill="{SAGE}" opacity="0.82" />

  <!-- the graph -->
  <g>
    {link(106, 332, 626, 176, GOLD, 3, 0.9)}
    {link(106, 332, 306, 178, GOLD, 1.5, 0.55)}
    {link(430, 250, 246, 266, GOLD, 1.5, 0.5)}
    {link(626, 176, 628, 145, CREAM, 2, 0.7)}
    {link(626, 176, 909, 151, CREAM, 2, 0.7)}
    {link(909, 151, 1090, 92, GOLD, 1.5, 0.58)}
    {link(246, 266, 306, 178, CREAM, 2, 0.7)}
    {link(1340, 246, 1400, 300, GOLD, 1.5, 0.5)}
  </g>

  <!-- a trace running the links -->
  <path d="{WALK_D}" fill="none" stroke="{CREAM}" stroke-width="2.6" stroke-linecap="round"
        stroke-dasharray="16 1040" opacity="0" class="trace" />

  <g>
    {node(106, 332, 4, GOLD, 0.95, "tw-a")}
    {node(246, 266, 10, GOLD, 1, "tw-b")}
    {node(306, 178, 7, SAGE, 1, "tw-c")}
    {node(430, 250, 5, GOLD, 1, "tw-f")}
    {node(626, 176, 9, LAV, 1, "tw-d")}
    {node(628, 145, 4, CREAM, 0.8, "tw-e")}
    {node(909, 151, 9, LAV, 1, "tw-f")}
    {node(1090, 92, 7, GOLD, 1, "tw-a")}
    {node(1340, 246, 8, NAVY_1, 0.7, "tw-c")}
    {node(1400, 300, 4, SAGE, 0.85, "tw-e")}
  </g>

  <!-- the bug, walking the graph -->
  <g class="bug-move">
    <g class="bug-hop">
      {BUG_BODY}
    </g>
  </g>

  <!-- handle, set in the same monospace the tools use -->
  <g font-family="{MONO}">
    <text x="101" y="112" font-size="21" letter-spacing="6.5" fill="{CREAM}" opacity="0.82">0xABCD01</text>
    <line x1="101" y1="130" x2="392" y2="130" stroke="{CREAM}" stroke-width="1.5" opacity="0.3" />
    <line x1="101" y1="142" x2="256" y2="142" stroke="{SAGE}" stroke-width="1.5" opacity="0.4" />
  </g>

  <!-- a terminal line, typing itself -->
  <g class="term-fade" font-family="{MONO}">
    <g clip-path="url(#typer)">
      <text x="101" y="392" font-size="16" fill="{GOLD}">$ ./recon --subs --live</text>
    </g>
    <!-- the cursor rides the typing edge -->
    <g clip-path="url(#typer)">
      <rect class="cursor" x="316" y="378" width="10" height="18" fill="{GOLD}" opacity="0.9" />
    </g>
  </g>

  <!-- sparkles -->
  {sparkle(690, 72, 1.0, CREAM, 0.8, "tw-a")}
  {sparkle(890, 278, 0.85, CREAM, 0.75, "tw-c")}
  {sparkle(1460, 92, 0.85, CREAM, 0.8, "tw-b")}
  {sparkle(1206, 120, 0.7, GOLD, 0.55, "tw-d")}
  {sparkle(1330, 330, 0.65, GOLD, 0.45, "tw-e")}
"""
    return svg(
        1600,
        420,
        body,
        "0xABCD01 profile banner",
        "A constellation graph in navy, cream, lavender, sage, and gold. A small bug walks "
        "the graph while a trace runs along the links.",
    )


# --------------------------------------------------------------- divider ----

DIVIDER_CSS = """
  @keyframes dtrace {
    0%   { stroke-dashoffset: 0;    opacity: 0; }
    10%  { opacity: 0.95; }
    90%  { opacity: 0.95; }
    100% { stroke-dashoffset: -246; opacity: 0; }
  }
  @keyframes dblink {
    0%, 100% { opacity: 0.45; }
    50%      { opacity: 1; }
  }
  .dtrace { animation: dtrace 3.6s linear infinite; }
  .d-a { animation: dblink 3.1s ease-in-out infinite; }
  .d-b { animation: dblink 3.8s ease-in-out 0.7s infinite; }
  .d-c { animation: dblink 4.4s ease-in-out 1.4s infinite; }
  .d-d { animation: dblink 3.4s ease-in-out 2.1s infinite; }
  .d-e { animation: dblink 4.0s ease-in-out 0.3s infinite; }
"""


def divider():
    body = f"""  <style>{DIVIDER_CSS}  </style>
  <g>
    <line x1="40" y1="22" x2="286" y2="22" stroke="{GOLD_D}" stroke-width="1.3" opacity="0.62" />
    <line x1="434" y1="22" x2="680" y2="22" stroke="{GOLD_D}" stroke-width="1.3" opacity="0.62" />
    <circle cx="40" cy="22" r="2.4" fill="{GOLD_D}" opacity="0.7" class="d-a" />
    <circle cx="680" cy="22" r="2.4" fill="{GOLD_D}" opacity="0.7" class="d-b" />
  </g>
  <g>
    {link(300, 14, 360, 22, GOLD_D, 1.8, 0.85)}
    {link(360, 22, 424, 13, GOLD_D, 1.8, 0.85)}
    {link(360, 22, 330, 31, GOLD_D, 1.5, 0.7)}
    {link(424, 13, 444, 26, GOLD_D, 1.3, 0.65)}
    {node(300, 14, 3.2, SAGE, 0.95, "d-a")}
    {node(360, 22, 5.4, GOLD, 1, "d-b")}
    {node(424, 13, 4.2, LAV, 0.98, "d-c")}
    {node(330, 31, 2.8, SAGE, 0.85, "d-d")}
    {node(444, 26, 2.6, GOLD, 0.78, "d-e")}
  </g>
  <!-- a pulse leaving the centre in both directions -->
  <line x1="286" y1="22" x2="40" y2="22" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"
        stroke-dasharray="12 234" opacity="0" class="dtrace" />
  {sparkle(276, 22, 0.55, GOLD_D, 0.7, "d-c")}
  {sparkle(468, 22, 0.55, GOLD_D, 0.7, "d-d")}
"""
    return svg(
        720,
        44,
        body,
        "Section divider",
        "A thin horizontal rule broken by a small constellation cluster, with a pulse "
        "travelling outward from the centre.",
    )


# ------------------------------------------------------------- tiny mark ----

MARK_CSS = """
  @keyframes mblink {
    0%, 100% { opacity: 0.3; }
    50%      { opacity: 1; }
  }
  .m-a { animation: mblink 3.4s ease-in-out infinite; }
  .m-b { animation: mblink 4.2s ease-in-out 0.8s infinite; }
  .m-c { animation: mblink 3.8s ease-in-out 1.6s infinite; }
  .m-d { animation: mblink 4.6s ease-in-out 0.4s infinite; }
"""


def mark():
    body = f"""  <style>{MARK_CSS}  </style>
  {link(6, 20, 26, 9, GOLD_D, 1.5, 0.7)}
  {link(26, 9, 46, 18, GOLD_D, 1.5, 0.7)}
  {link(26, 9, 30, 30, GOLD_D, 1.2, 0.55)}
  {node(6, 20, 2.6, SAGE, 0.9, "m-a")}
  {node(26, 9, 4.4, GOLD, 1, "m-b")}
  {node(46, 18, 3.4, LAV, 0.95, "m-c")}
  {node(30, 30, 2.2, SAGE, 0.8, "m-d")}
  {sparkle(50, 32, 0.45, GOLD_D, 0.6, "m-a")}
"""
    return svg(
        58,
        40,
        body,
        "Constellation mark",
        "Three linked nodes with a small sparkle, blinking gently.",
    )


# --------------------------------------------------------- section icons ----

ICON_CSS = """
  @keyframes iglow {
    0%, 100% { opacity: 0.72; }
    50%      { opacity: 1; }
  }
  .iglow { animation: iglow 4.6s ease-in-out infinite; }
"""


def badge(glyph, title, delay=0):
    """Rounded chip with a glyph. The chip carries its own dark fill, so the
    icon stays legible on both the light and the dark GitHub theme."""
    body = f"""  <style>{ICON_CSS}  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NAVY_1}" />
      <stop offset="1" stop-color="{NAVY_2}" />
    </linearGradient>
  </defs>
  <rect x="0.75" y="0.75" width="26.5" height="26.5" rx="8" fill="url(#bg)" stroke="{GOLD}" stroke-opacity="0.45" stroke-width="1.5" />
  <g class="iglow" style="animation-delay:{delay}s">{glyph}</g>
"""
    return svg(
        28,
        28,
        body,
        title,
        "A small rounded chip with a gold glyph.",
    )


def icon_research():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.5" fill="none" opacity="0.95" stroke-linecap="round">
    <path d="M7.5 19.5 L14 8 L20.5 19.5" />
    <path d="M10.5 19.5 L14 14 L17.5 19.5" />
  </g>
  {node(14, 8, 2.4, GOLD)}
  {node(7.5, 19.5, 1.9, SAGE)}
  {node(20.5, 19.5, 1.9, SAGE)}
  {node(14, 14, 1.7, LAV)}
"""
    return badge(glyph, "Research icon")


def icon_tools():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.7" fill="none" opacity="0.95" stroke-linecap="round" stroke-linejoin="round">
    <path d="M8 10 L12.5 14 L8 18" />
    <path d="M14.5 18.5 H20" />
  </g>
  {sparkle(20.5, 9.5, 0.5, LAV, 0.9)}
"""
    return badge(glyph, "Tools icon", 0.8)


def icon_now():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.6" fill="none" opacity="0.95" stroke-linecap="round">
    <circle cx="14" cy="14" r="8.2" />
    <path d="M14 9.4 V14 L17.4 16.2" />
  </g>
  {node(14, 9.4, 1.6, GOLD)}
  {node(14, 14, 1.7, LAV)}
"""
    return badge(glyph, "Currently icon", 1.6)


def icon_contact():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.5" fill="none" opacity="0.95" stroke-linecap="round">
    <path d="M8 20 A8.5 8.5 0 0 1 8 8" />
    <path d="M12 21 A12 12 0 0 1 12 7" />
    <path d="M16 22 A15.5 15.5 0 0 1 16 6" />
  </g>
  {node(7.5, 14, 2.8, GOLD)}
  {sparkle(20, 12, 0.42, LAV, 0.85)}
"""
    return badge(glyph, "Contact icon", 2.4)


# ------------------------------------------------------------ role strip ----

ROLES_CSS = """
  @keyframes rglow {
    0%, 100% { opacity: 0.8; }
    50%      { opacity: 1; }
  }
  .r-a { animation: rglow 4.1s ease-in-out infinite; }
  .r-b { animation: rglow 4.8s ease-in-out 0.6s infinite; }
  .r-c { animation: rglow 5.3s ease-in-out 1.2s infinite; }
  .r-d { animation: rglow 3.9s ease-in-out 0.3s infinite; }
"""


def chip(x, w, label, glyph, accent, cls):
    inner = (
        f'<g transform="translate({x + 11} 11) scale(0.52)">{glyph}</g>'
        f'<text x="{x + 34}" y="24" font-family="{MONO}" font-size="13.5" letter-spacing="0.4" '
        f'fill="{CREAM}" opacity="0.92">{label}</text>'
    )
    return (
        f'<g class="{cls}"><rect x="{x}" y="0.5" width="{w}" height="31" rx="15.5" '
        f'fill="{NAVY_1}" fill-opacity="0.92" stroke="{accent}" stroke-opacity="0.5" '
        f'stroke-width="1.4"/>{inner}</g>'
    )


def role_strip():
    bug_glyph = (
        f'<g stroke="{GOLD}" stroke-width="1.7" fill="none" stroke-linecap="round">'
        f'<rect x="10" y="10" width="10" height="12" rx="5" />'
        f'<path d="M10 14.5 H6.5 M10 18 H6.5 M20 14.5 H23.5 M20 18 H23.5 '
        f'M13 10 V6.5 M17 10 V6.5" /></g>'
    )
    impact_glyph = (
        f'<g stroke="{GOLD}" stroke-width="1.8" fill="none" stroke-linecap="round" '
        f'stroke-linejoin="round"><path d="M15 5 L23 9.5 V20 H7 V9.5 Z" />'
        f'<path d="M11.5 20 V14 H18.5 V20" /></g>'
    )
    research_glyph = (
        f'<g stroke="{GOLD}" stroke-width="1.7" fill="none" stroke-linecap="round">'
        f'<path d="M7 20 L14.5 7 L22 20" /><path d="M10.5 20 L14.5 14 L18.5 20" /></g>'
    )
    body = f"""  <style>{ROLES_CSS}  </style>
  {chip(0, 132, "bug bounty", bug_glyph, GOLD, "r-a")}
  {chip(146, 118, "pentest", impact_glyph, SAGE, "r-b")}
  {chip(278, 96, "osint", research_glyph, LAV, "r-c")}
  {sparkle(392, 15, 0.55, GOLD, 0.75, "r-d")}
"""
    return svg(
        410,
        32,
        body,
        "Areas of work",
        "Three chips: bug bounty, pentest, OSINT.",
    )


# ----------------------------------------------------------------- write ----

def write(name, content):
    path = os.path.join(ASSETS, name)
    with open(path, "w") as fh:
        fh.write(content)
    print(f"wrote {path} ({len(content)} bytes)")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    write("profile-banner.svg", banner())
    write("divider.svg", divider())
    write("mark.svg", mark())
    write("icon-research.svg", icon_research())
    write("icon-tools.svg", icon_tools())
    write("icon-now.svg", icon_now())
    write("icon-contact.svg", icon_contact())
    write("roles.svg", role_strip())


if __name__ == "__main__":
    main()
