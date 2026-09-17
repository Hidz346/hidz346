#!/usr/bin/env python3
"""Generate a polished animated GitHub profile card as a self-contained SVG."""

from __future__ import annotations

import glob
import html
import os
import sys
from pathlib import Path


DISPLAY_NAME = os.environ.get("PROFILE_NAME") or "SYAHID SUBHAN PUTRA"
LOGIN = os.environ.get("GITHUB_LOGIN") or "your-username"
TOKEN = os.environ.get("GITHUB_TOKEN") or ""
OUT_PATH = Path(os.environ.get("OUT_PATH") or "assets/profile.svg")
AVATAR_PATH = os.environ.get("AVATAR_PATH") or ""

ROLE = os.environ.get("PROFILE_ROLE") or "Web Developer & Security Enthusiast"
LOCATION = os.environ.get("PROFILE_LOCATION") or "Indonesia"
BRAND = os.environ.get("PROFILE_BRAND") or "HIDZ PROJECT"
WEBSITE = os.environ.get("PROFILE_WEBSITE") or ""
CONTACT = os.environ.get("PROFILE_CONTACT") or ""

PROFILE_FIELDS = [
    ("ROLE", ROLE),
    ("LOCATION", LOCATION),
    ("FOCUS", "Web development, automation & security"),
    ("FRONTEND", "HTML, CSS, JavaScript"),
    ("BACKEND", "PHP, Node.js, Python"),
    ("DATABASE", "MySQL, PostgreSQL, SQLite"),
    ("TOOLING", "Git, GitHub, Linux, VS Code"),
]

PROMPT_COMMANDS = [
    "whoami",
    "build --clean --fast",
    "ship something useful",
    "stay curious",
]

# Visual system: dark graphite + electric cyan + restrained amber.
BG = "#070b12"
PANEL = "#0c121c"
PANEL_2 = "#101927"
GRID = "#172335"
BORDER = "#26354b"
TEXT = "#e8f0f7"
MUTED = "#718096"
CYAN = "#49e6ff"
CYAN_SOFT = "#8cf3ff"
AMBER = "#ffb454"
GREEN = "#4ade80"

RAMP = " .,:;irsXA253hMHGS#9B&@"
ART_COLS = 48
CELL_W = 8.0
CELL_H = 13.5
TITLEBAR_H = 42


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def find_avatar() -> str | None:
    if AVATAR_PATH and Path(AVATAR_PATH).is_file():
        return AVATAR_PATH
    for pattern in ("assets/avatar.*", "avatar.*", ".github/avatar.*"):
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def ascii_rows_from_image(path: str) -> list[str]:
    from PIL import Image, ImageOps
    import numpy as np

    image = Image.open(path).convert("RGB")
    # The source image has a bright, detailed background. A centered crop plus
    # a luminance gate keeps the person readable instead of turning the whole
    # scene into noisy characters.
    side = int(min(image.size) * 0.78)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    gray = gray.resize((ART_COLS, 68), Image.Resampling.LANCZOS)

    pixels = np.asarray(gray, dtype=np.float32) / 255.0
    threshold = 0.30
    rows: list[str] = []
    for row in pixels:
        line = []
        for value in row:
            if value < threshold:
                line.append(" ")
                continue
            index = min(7, int((value - threshold) / (1.0 - threshold) * 7))
            line.append(" .:+*#%@"[index])
        rows.append("".join(line))
    return rows


def ascii_rows_placeholder() -> list[str]:
    """Stable fallback portrait made without randomness."""
    rows: list[str] = []
    for y in range(68):
        line = []
        for x in range(ART_COLS):
            nx = (x - ART_COLS / 2) / (ART_COLS / 2)
            ny = (y - 31) / 34
            head = ((nx / 0.48) ** 2 + ((ny + 0.14) / 0.48) ** 2) < 1
            shoulders = ((nx / 0.88) ** 2 + ((ny - 0.55) / 0.42) ** 2) < 1
            if head or shoulders:
                density = (abs(nx) + abs(ny)) / 2
                line.append("#" if density < 0.28 else "+")
            else:
                line.append(" ")
        rows.append("".join(line))
    return rows


def fetch_github_stats(login: str, token: str) -> dict[str, str]:
    empty = {
        "repos": "—",
        "stars": "—",
        "followers": "—",
        "contributions": "—",
        "languages": "—",
    }
    if not login or login == "your-username":
        return empty

    try:
        import requests

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-profile-card-generator",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        user = requests.get(
            f"https://api.github.com/users/{login}", headers=headers, timeout=12
        )
        user.raise_for_status()
        profile = user.json()

        stats = {
            "repos": str(profile.get("public_repos", "—")),
            "stars": "0",
            "followers": str(profile.get("followers", "—")),
            "contributions": "—",
            "languages": "—",
        }

        repos: list[dict] = []
        for page in range(1, 11):
            response = requests.get(
                f"https://api.github.com/users/{login}/repos",
                params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
                headers=headers,
                timeout=12,
            )
            response.raise_for_status()
            batch = response.json()
            repos.extend(batch)
            if len(batch) < 100:
                break

        stats["stars"] = str(sum(int(repo.get("stargazers_count", 0)) for repo in repos))

        language_counts: dict[str, int] = {}
        for repo in repos:
            language = repo.get("language")
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        if language_counts:
            top = sorted(language_counts, key=language_counts.get, reverse=True)[:4]
            stats["languages"] = " / ".join(top)

        if token:
            query = """
            query($login: String!) {
              user(login: $login) {
                contributionsCollection {
                  contributionCalendar { totalContributions }
                }
              }
            }
            """
            response = requests.post(
                "https://api.github.com/graphql",
                headers=headers,
                json={"query": query, "variables": {"login": login}},
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
            total = (
                payload.get("data", {})
                .get("user", {})
                .get("contributionsCollection", {})
                .get("contributionCalendar", {})
                .get("totalContributions")
            )
            if total is not None:
                stats["contributions"] = str(total)

        return stats
    except Exception as exc:  # Keep generation alive even when GitHub is unavailable.
        print(f"warning: GitHub stats unavailable: {exc}", file=sys.stderr)
        return empty


def typing_animation(commands: list[str], x: float, y: float) -> tuple[str, str, str, str, float]:
    """Return a reliable terminal prompt with a blinking cursor.

    The original template animated several overlapping SVG text nodes. That can
    render as blank/overlapping text in static SVG renderers. A single command
    keeps the card deterministic everywhere while retaining subtle motion.
    """
    command = commands[0] if commands else "whoami"
    width = max(1, len(command)) * 8.7
    style = (
        "@keyframes blink { 0%,49% { opacity: 1; } 50%,100% { opacity: 0; } } "
        ".cursor { animation: blink 1s steps(1) infinite; }"
    )
    text = (
        f'<text x="{x:.1f}" y="{y:.1f}" class="command" '
        f'textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs">{esc(command)}</text>'
    )
    cursor = f'<rect x="{x + width + 5:.1f}" y="{y - 15:.1f}" width="7" height="17" class="cursor"/>'
    return style, "", text, cursor, width


def build_svg(art_rows: list[str], stats: dict[str, str]) -> str:
    width = 1180
    art_x = 54
    art_y = 125
    art_w = ART_COLS * CELL_W
    art_h = len(art_rows) * CELL_H
    right_x = 470
    right_w = width - right_x - 54

    fields = PROFILE_FIELDS + [
        ("GITHUB", LOGIN if LOGIN != "your-username" else "set GITHUB_LOGIN"),
        ("LANGUAGES", stats["languages"]),
    ]

    # Dynamic height keeps long profile values from colliding with the footer.
    field_h = 33
    fields_top = 160
    stats_y = fields_top + len(fields) * field_h + 30
    prompt_y = max(art_y + art_h + 34, stats_y + 145)
    height = prompt_y + 100

    animation_style, prompt_defs, prompt_text, prompt_cursor, prompt_width = typing_animation(
        PROMPT_COMMANDS, 120, prompt_y + 44
    )

    art_svg = []
    for i, row in enumerate(art_rows):
        y = art_y + i * CELL_H
        art_svg.append(
            f'<text x="{art_x}" y="{y:.1f}" class="ascii" style="animation-delay:{i * 0.018:.3f}s">'
            f'{esc(row)}</text>'
        )

    field_svg = []
    for i, (label, value) in enumerate(fields):
        y = fields_top + i * field_h
        field_svg.append(
            f'<g class="field" style="animation-delay:{0.25 + i * 0.055:.2f}s">'
            f'<text x="{right_x}" y="{y}" class="label">{esc(label)}</text>'
            f'<text x="{right_x + 145}" y="{y}" class="value">{esc(value)}</text>'
            f'</g>'
        )

    stat_items = [
        ("REPOSITORIES", stats["repos"]),
        ("STARS", stats["stars"]),
        ("FOLLOWERS", stats["followers"]),
        ("CONTRIBUTIONS", stats["contributions"]),
    ]
    stat_w = 150
    stat_gap = 14
    stat_svg = []
    for i, (label, value) in enumerate(stat_items):
        x = right_x + i * (stat_w + stat_gap)
        stat_svg.append(
            f'<g class="stat" style="animation-delay:{1.0 + i * 0.1:.2f}s">'
            f'<rect x="{x}" y="{stats_y}" width="{stat_w}" height="86" rx="10" fill="{PANEL_2}" stroke="{BORDER}"/>'
            f'<text x="{x + 14}" y="{stats_y + 27}" class="stat-label">{esc(label)}</text>'
            f'<text x="{x + 14}" y="{stats_y + 61}" class="stat-value">{esc(value)}</text>'
            f'</g>'
        )

    # A compact footer lets the card stand alone without relying on external badges.
    footer_text = f"{BRAND}  //  OPEN SOURCE  //  {DISPLAY_NAME}"
    if WEBSITE:
        footer_text += f"  //  {WEBSITE}"
    if CONTACT:
        footer_text += f"  //  {CONTACT}"

    title = f"{LOGIN}@github: ~/profile"
    name = DISPLAY_NAME.upper()

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(DISPLAY_NAME)} — GitHub profile</title>
  <desc id="desc">Animated terminal-inspired developer profile card.</desc>
  <defs>
    <linearGradient id="bgGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.10"/>
      <stop offset="0.48" stop-color="{BG}" stop-opacity="0"/>
      <stop offset="1" stop-color="{AMBER}" stop-opacity="0.08"/>
    </linearGradient>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0H0V28" fill="none" stroke="{GRID}" stroke-width="1"/>
    </pattern>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{CYAN_SOFT}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{CYAN_SOFT}" stop-opacity="0.18"/>
      <stop offset="1" stop-color="{CYAN_SOFT}" stop-opacity="0"/>
    </linearGradient>
    <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="artClip"><rect x="28" y="82" width="380" height="{art_h + 70:.0f}" rx="16"/></clipPath>
    <style>
      .mono {{ font-family: "SFMono-Regular", "Cascadia Code", "Roboto Mono", Consolas, monospace; }}
      .ascii {{ font-family: "Courier New", monospace; font-size: {CELL_H * 0.82:.1f}px; fill: {CYAN_SOFT}; white-space: pre; opacity: 1; animation: reveal .35s steps(1) forwards; }}
      .field {{ opacity: 1; animation: reveal .35s steps(1) forwards; }}
      .label {{ font: 700 12px "SFMono-Regular", Consolas, monospace; fill: {MUTED}; letter-spacing: 1.2px; }}
      .value {{ font: 500 15px "SFMono-Regular", Consolas, monospace; fill: {TEXT}; }}
      .stat {{ opacity: 1; animation: reveal .35s steps(1) forwards; }}
      .stat-label {{ font: 700 10px "SFMono-Regular", Consolas, monospace; fill: {MUTED}; letter-spacing: 1.3px; }}
      .stat-value {{ font: 700 25px "SFMono-Regular", Consolas, monospace; fill: {CYAN_SOFT}; }}
      .command {{ font: 600 16px "SFMono-Regular", Consolas, monospace; fill: {CYAN_SOFT}; }}
      .cursor {{ fill: {CYAN}; filter: url(#softGlow); }}
      .scanline {{ animation: scan 4.8s linear infinite; }}
      .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-origin: center; }}
      {animation_style}
      @keyframes reveal {{ from {{ opacity: .35; }} to {{ opacity: 1; }} }}
      @keyframes scan {{ from {{ transform: translateY(0); }} to {{ transform: translateY({height - 70}px); }} }}
      @keyframes pulse {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: .85; }} }}
      @media (prefers-reduced-motion: reduce) {{ .ascii,.field,.stat,.scanline,.pulse,.cursor,.command {{ animation: none !important; opacity: 1 !important; }} }}
    </style>
    {prompt_defs}
  </defs>

  <rect width="{width}" height="{height}" rx="18" fill="{BG}"/>
  <rect width="{width}" height="{height}" rx="18" fill="url(#bgGlow)"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="17" fill="none" stroke="{BORDER}"/>
  <rect x="20" y="20" width="{width - 40}" height="{height - 40}" rx="13" fill="url(#grid)" opacity="0.58"/>

  <!-- Window chrome -->
  <rect x="20" y="20" width="{width - 40}" height="{TITLEBAR_H}" rx="13" fill="{PANEL}" stroke="{BORDER}"/>
  <circle cx="45" cy="41" r="6" fill="#ff5f57"/>
  <circle cx="66" cy="41" r="6" fill="#febc2e"/>
  <circle cx="87" cy="41" r="6" fill="#28c840"/>
  <text x="{width / 2:.0f}" y="46" text-anchor="middle" class="mono" font-size="12" fill="{MUTED}">{esc(title)}</text>

  <!-- Identity -->
  <text x="54" y="96" class="mono" font-size="11" font-weight="700" fill="{CYAN}" letter-spacing="2">PROFILE / 001</text>
  <text x="{right_x}" y="98" class="mono" font-size="29" font-weight="800" fill="{TEXT}">{esc(name)}</text>
  <text x="{right_x}" y="122" class="mono" font-size="13" fill="{CYAN}" letter-spacing="1.4">{esc(ROLE.upper())}</text>

  <!-- Portrait / ASCII panel -->
  <rect x="28" y="82" width="380" height="{art_h + 70:.0f}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
  <g clip-path="url(#artClip)">{''.join(art_svg)}</g>
  <rect x="28" y="82" width="380" height="{art_h + 70:.0f}" rx="16" fill="none" stroke="{CYAN}" stroke-opacity="0.22"/>
  <rect x="28" y="82" width="380" height="{art_h + 70:.0f}" rx="16" fill="url(#scan)" opacity="0.35" class="scanline"/>
  <circle cx="54" cy="{art_y + art_h + 24:.0f}" r="4" fill="{GREEN}" class="pulse"/>
  <text x="66" y="{art_y + art_h + 28:.0f}" class="mono" font-size="11" fill="{MUTED}">SYSTEM ONLINE / ASCII AVATAR</text>

  <!-- Profile data -->
  <line x1="{right_x}" y1="139" x2="{width - 54}" y2="139" stroke="{CYAN}" stroke-opacity="0.38"/>
  {''.join(field_svg)}

  <!-- Stats -->
  {''.join(stat_svg)}

  <!-- Terminal prompt -->
  <rect x="54" y="{prompt_y}" width="{width - 108}" height="72" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
  <text x="72" y="{prompt_y + 25}" class="mono" font-size="11" font-weight="700" fill="{MUTED}">terminal://profile</text>
  <text x="72" y="{prompt_y + 48}" class="mono" font-size="15" font-weight="700" fill="{AMBER}">$</text>
  {prompt_text}
  {prompt_cursor}

  <!-- Footer -->
  <text x="54" y="{height - 17}" class="mono" font-size="9" fill="{MUTED}" letter-spacing="1">{esc(footer_text)}</text>
</svg>
'''


def main() -> None:
    avatar = find_avatar()
    if avatar:
        print(f"using avatar: {avatar}")
        art = ascii_rows_from_image(avatar)
    else:
        print("warning: no avatar found; using fallback silhouette", file=sys.stderr)
        art = ascii_rows_placeholder()

    stats = fetch_github_stats(LOGIN, TOKEN)
    svg = build_svg(art, stats)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
