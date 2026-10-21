#!/usr/bin/env python3
"""Generate SVG decorations for the 0xABCD01 profile README.

Visual language: a constellation graph. Nodes are targets, links are the
connections between them. Palette is inherited from the original banner
(navy / cream / lavender / sage / gold) so the whole profile reads as one
system.

Decorations carry no text. Section headings stay plain text so they remain
readable in a screen reader and in a terminal.
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


def sparkle(x, y, s=1.0, fill=LAV, op=0.85):
    return (
        f'<path d="M {x} {y - 6 * s} C {x} {y - 2 * s} {x + 2 * s} {y} {x + 6 * s} {y} '
        f'C {x + 2 * s} {y} {x} {y + 2 * s} {x} {y + 6 * s} '
        f'C {x} {y + 2 * s} {x - 2 * s} {y} {x - 6 * s} {y} '
        f'C {x - 2 * s} {y} {x} {y - 2 * s} {x} {y - 6 * s} Z" '
        f'fill="{fill}" opacity="{op}"/>'
    )


def node(x, y, r, fill, op=1.0):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" opacity="{op}"/>'


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

def banner():
    body = f"""  <defs>
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
  </defs>

  <rect width="1600" height="420" rx="28" fill="url(#wash)" />
  <rect x="930" y="0" width="670" height="420" fill="url(#dots)" opacity="0.5" />

  <!-- cave mouth -->
  <path d="M1010 420C1010 185 1160 48 1374 48c115 0 174 38 226 92v280z" fill="url(#cream)" opacity="0.96" />
  <path d="M1118 420c0-157 101-268 247-268 86 0 153 37 235 111v157z" fill="{LAV}" opacity="0.75" />
  <path d="M1244 420c0-94 63-166 147-166 79 0 147 62 209 143v23z" fill="{SAGE}" opacity="0.82" />

  <!-- constellation: the graph that connects targets to findings -->
  <g>
    {link(106, 332, 626, 176, GOLD, 3, 0.9)}
    {link(106, 332, 306, 178, GOLD, 1.5, 0.55)}
    {link(626, 176, 628, 145, CREAM, 2, 0.7)}
    {link(626, 176, 909, 151, CREAM, 2, 0.7)}
    {link(909, 151, 1090, 92, GOLD, 1.5, 0.58)}
    {link(306, 178, 246, 266, CREAM, 2, 0.7)}
    {link(246, 266, 306, 178, CREAM, 2, 0.7)}
    {link(1340, 246, 1400, 300, GOLD, 1.5, 0.5)}
    {node(106, 332, 4, GOLD, 0.95)}
    {node(246, 266, 10, GOLD)}
    {node(306, 178, 7, SAGE)}
    {node(626, 176, 9, LAV)}
    {node(628, 145, 4, CREAM, 0.8)}
    {node(909, 151, 9, LAV)}
    {node(1090, 92, 7, GOLD)}
    {node(1340, 246, 8, NAVY_1, 0.7)}
    {node(1400, 300, 4, SAGE, 0.85)}
  </g>

  <!-- handle, set in the same monospace the tools use -->
  <g font-family="'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace">
    <text x="101" y="112" font-size="21" letter-spacing="6.5" fill="{CREAM}" opacity="0.82">0xABCD01</text>
    <line x1="101" y1="130" x2="392" y2="130" stroke="{CREAM}" stroke-width="1.5" opacity="0.3" />
    <line x1="101" y1="142" x2="256" y2="142" stroke="{SAGE}" stroke-width="1.5" opacity="0.4" />
  </g>

  <!-- sparkles -->
  {sparkle(690, 72, 1.0, CREAM, 0.8)}
  {sparkle(890, 278, 0.85, CREAM, 0.75)}
  {sparkle(1460, 92, 0.85, CREAM, 0.8)}
  {sparkle(1206, 120, 0.7, GOLD, 0.55)}
  {sparkle(1330, 330, 0.65, GOLD, 0.45)}
"""
    return svg(
        1600,
        420,
        body,
        "0xABCD01 profile banner",
        "A constellation graph in navy, cream, lavender, sage, and gold, with the handle set in monospace.",
    )


# --------------------------------------------------------------- divider ----

def divider():
    """Horizontal rule with a small constellation cluster at its centre."""
    body = f"""  <g opacity="0.9">
    <line x1="40" y1="22" x2="286" y2="22" stroke="{GOLD_D}" stroke-width="1.3" opacity="0.62" />
    <line x1="434" y1="22" x2="680" y2="22" stroke="{GOLD_D}" stroke-width="1.3" opacity="0.62" />
    <circle cx="40" cy="22" r="2.4" fill="{GOLD_D}" opacity="0.7" />
    <circle cx="680" cy="22" r="2.4" fill="{GOLD_D}" opacity="0.7" />
  </g>
  <g>
    {link(300, 14, 360, 22, GOLD_D, 1.8, 0.85)}
    {link(360, 22, 424, 13, GOLD_D, 1.8, 0.85)}
    {link(360, 22, 330, 31, GOLD_D, 1.5, 0.7)}
    {link(424, 13, 444, 26, GOLD_D, 1.3, 0.65)}
    {node(300, 14, 3.2, SAGE, 0.95)}
    {node(360, 22, 5.4, GOLD)}
    {node(424, 13, 4.2, LAV, 0.98)}
    {node(330, 31, 2.8, SAGE, 0.85)}
    {node(444, 26, 2.6, GOLD, 0.78)}
  </g>
  {sparkle(276, 22, 0.55, GOLD_D, 0.7)}
  {sparkle(468, 22, 0.55, GOLD_D, 0.7)}
"""
    return svg(
        720,
        44,
        body,
        "Section divider",
        "A thin horizontal rule broken by a small constellation cluster.",
    )


# ------------------------------------------------------------- tiny mark ----

def mark():
    """Compact cluster used in tight spaces, such as the contact block."""
    body = f"""  {link(6, 20, 26, 9, GOLD_D, 1.5, 0.7)}
  {link(26, 9, 46, 18, GOLD_D, 1.5, 0.7)}
  {link(26, 9, 30, 30, GOLD_D, 1.2, 0.55)}
  {node(6, 20, 2.6, SAGE, 0.9)}
  {node(26, 9, 4.4, GOLD)}
  {node(46, 18, 3.4, LAV, 0.95)}
  {node(30, 30, 2.2, SAGE, 0.8)}
  {sparkle(50, 32, 0.45, GOLD_D, 0.6)}
"""
    return svg(
        58,
        40,
        body,
        "Constellation mark",
        "Three linked nodes with a small sparkle.",
    )


# --------------------------------------------------------- section icons ----

def badge(glyph, title):
    """Rounded chip with a glyph. The chip carries its own dark fill, so the
    icon stays legible on both the light and the dark GitHub theme."""
    body = f"""  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NAVY_1}" />
      <stop offset="1" stop-color="{NAVY_2}" />
    </linearGradient>
  </defs>
  <rect x="0.75" y="0.75" width="26.5" height="26.5" rx="8" fill="url(#bg)" stroke="{GOLD}" stroke-opacity="0.45" stroke-width="1.5" />
  {glyph}
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
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.95">
    <path d="M8 10 L12.5 14 L8 18" />
    <path d="M14.5 18.5 H20" />
  </g>
  {sparkle(20.5, 9.5, 0.5, LAV, 0.9)}
"""
    return badge(glyph, "Tools icon")


def icon_now():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.6" fill="none" opacity="0.95" stroke-linecap="round">
    <circle cx="14" cy="14" r="8.2" />
    <path d="M14 9.4 V14 L17.4 16.2" />
  </g>
  {node(14, 9.4, 1.6, GOLD)}
  {node(14, 14, 1.7, LAV)}
"""
    return badge(glyph, "Currently icon")


def icon_contact():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.5" fill="none" opacity="0.95" stroke-linecap="round">
    <path d="M8 20 A8.5 8.5 0 0 1 8 8" />
    <path d="M12 21 A12 12 0 0 1 12 7" />
    <path d="M16 22 A15.5 15.5 0 0 1 16 6" />
  </g>
  {node(7.5, 14, 2.8, GOLD)}
  {sparkle(20, 12, 0.42, LAV, 0.85)}
"""
    return badge(glyph, "Contact icon")


def icon_bug():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.5" fill="none" opacity="0.95" stroke-linecap="round">
    <rect x="9.5" y="9.5" width="9" height="11" rx="4.5" />
    <path d="M9.5 13.5 H6.5 M9.5 17 H6.5 M18.5 13.5 H21.5 M18.5 17 H21.5 M12 9.5 V6.5 M16 9.5 V6.5" />
  </g>
  {node(12, 6, 1.5, SAGE)}
  {node(16, 6, 1.5, SAGE)}
  {sparkle(21, 9, 0.4, LAV, 0.85)}
"""
    return badge(glyph, "Bug bounty icon")


def icon_impact():
    glyph = f"""  <g stroke="{GOLD}" stroke-width="1.6" fill="none" opacity="0.95" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 5.5 L21 9.5 V18.5 H7 V9.5 Z" />
    <path d="M11 18.5 V13.5 H17 V18.5" />
  </g>
  {node(14, 5.5, 2.4, GOLD)}
  {sparkle(22.5, 7, 0.42, LAV, 0.9)}
"""
    return badge(glyph, "Impact icon")


# ------------------------------------------------------------ role strip ----

def chip(x, w, label, glyph, accent):
    """A rounded chip holding a small glyph and a word."""
    inner = (
        f'<g transform="translate({x + 11} 11) scale(0.52)">{glyph}</g>'
        f'<text x="{x + 34}" y="24" font-family="\'SFMono-Regular\',Consolas,'
        f'\'Liberation Mono\',Menlo,monospace" font-size="13.5" letter-spacing="0.4" '
        f'fill="{CREAM}" opacity="0.92">{label}</text>'
    )
    return (
        f'<g><rect x="{x}" y="0.5" width="{w}" height="31" rx="15.5" '
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
    body = f"""  {chip(0, 132, "bug bounty", bug_glyph, GOLD)}
  {chip(146, 118, "pentest", impact_glyph, SAGE)}
  {chip(278, 96, "osint", research_glyph, LAV)}
  {sparkle(392, 15, 0.55, GOLD, 0.75)}
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
