from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
OUT_PATH = ROOT / os.getenv("OUT_PATH", "assets/profile.gif")
AVATAR_PATH = ROOT / os.getenv("AVATAR_PATH", "assets/hacker.jpg")
LOGIN = os.getenv("GITHUB_LOGIN", "Hidz346").strip()
NAME = os.getenv("PROFILE_NAME", "SYAHID SUBHAN PUTRA")
BRAND = os.getenv("PROFILE_BRAND", "HIDZ PROJECT")
ROLE = os.getenv("PROFILE_ROLE", "WEB DEVELOPER & SECURITY ENTHUSIAST")
LOCATION = os.getenv("PROFILE_LOCATION", "INDONESIA")

W, H = 1000, 583
FPS = 8
FRAMES = 36
BG = (6, 10, 16)
PANEL = (10, 17, 27)
LINE = (33, 48, 68)
CYAN = (73, 230, 255)
AMBER = (255, 180, 84)
WHITE = (232, 240, 247)
MUTED = (120, 139, 160)
GREEN = (74, 222, 128)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_MONO = FONT_DIR / "DejaVuSansMono.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSansMono-Bold.ttf"


def font(size: int, bold: bool = False):
    path = FONT_BOLD if bold else FONT_MONO
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def fetch_stats() -> dict[str, Any]:
    empty = {"repos": "—", "stars": "—", "followers": "—", "following": "—", "languages": "—"}
    if not LOGIN:
        return empty
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "syahid-profile-card"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        user = requests.get(f"https://api.github.com/users/{LOGIN}", headers=headers, timeout=12)
        user.raise_for_status()
        data = user.json()
        repos = requests.get(
            f"https://api.github.com/users/{LOGIN}/repos?per_page=100&sort=updated",
            headers=headers,
            timeout=12,
        )
        repos.raise_for_status()
        repo_items = repos.json()
        stars = sum(int(repo.get("stargazers_count", 0)) for repo in repo_items)
        languages: dict[str, int] = {}
        for repo in repo_items:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        top_lang = max(languages, key=languages.get) if languages else "—"
        return {
            "repos": str(data.get("public_repos", 0)),
            "stars": str(stars),
            "followers": str(data.get("followers", 0)),
            "following": str(data.get("following", 0)),
            "languages": top_lang,
        }
    except (requests.RequestException, ValueError, TypeError):
        return empty


def load_avatar() -> Image.Image:
    try:
        img = Image.open(AVATAR_PATH).convert("RGB")
    except (FileNotFoundError, OSError):
        img = Image.new("RGB", (1024, 1024), (10, 16, 24))
        d = ImageDraw.Draw(img)
        d.ellipse((250, 120, 774, 644), outline=CYAN, width=12)
        d.text((310, 700), "HIDZ", fill=CYAN, font=font(90, True))
    return ImageOps.fit(img, (440, 440), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def glow_layer(size, box, color, blur=18, alpha=100):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=20, outline=(*color, alpha), width=5)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def draw_wrapped_text(draw, text, xy, max_width, fnt, fill, spacing=5):
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def render_frame(frame: int, avatar: Image.Image, stats: dict[str, Any]) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)

    # Background grid and subtle moving scanline.
    for x in range(0, W, 32):
        draw.line((x, 0, x, H), fill=(13, 24, 36), width=1)
    for y in range(0, H, 32):
        draw.line((0, y, W, y), fill=(13, 24, 36), width=1)
    scan_y = (frame * 15) % H
    draw.line((0, scan_y, W, scan_y), fill=(49, 131, 157), width=1)

    # Outer shell.
    draw.rounded_rectangle((18, 18, W - 18, H - 18), radius=22, fill=PANEL, outline=LINE, width=2)
    draw.rounded_rectangle((32, 32, W - 32, H - 32), radius=16, outline=(25, 38, 54), width=1)

    # Header.
    draw.rounded_rectangle((32, 32, W - 32, 78), radius=16, fill=(9, 15, 23), outline=LINE, width=1)
    draw.ellipse((52, 50, 64, 62), fill=(255, 95, 87))
    draw.ellipse((74, 50, 86, 62), fill=(254, 188, 46))
    draw.ellipse((96, 50, 108, 62), fill=(40, 200, 64))
    title = f"{LOGIN or 'github-user'}@profile: ~/HIDZ"
    draw.text((W // 2, 55), title, anchor="mm", font=font(15), fill=MUTED)

    # Avatar panel.
    ax1, ay1, ax2, ay2 = 40, 96, 485, 536
    glow = glow_layer((W, H), (ax1, ay1, ax2, ay2), CYAN, 22, 85)
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((ax1, ay1, ax2, ay2), radius=18, fill=(4, 8, 13), outline=(45, 91, 111), width=2)

    # Slightly animated image treatment.
    avatar_frame = avatar.copy()
    pulse = 1.0 + 0.008 * ((frame % 20) / 10 - 1 if frame % 20 < 10 else (20 - frame % 20) / 10 - 1)
    size = int(440 * pulse), int(440 * pulse)
    avatar_frame = avatar_frame.resize(size, Image.Resampling.LANCZOS)
    ox = ax1 + (ax2 - ax1 - size[0]) // 2
    oy = ay1 + (ay2 - ay1 - size[1]) // 2
    im.paste(avatar_frame, (ox, oy))
    draw = ImageDraw.Draw(im)
    draw.rectangle((ax1, ay2 - 54, ax2, ay2), fill=(5, 10, 16))
    draw.text((68, ay2 - 40), "●  SYSTEM ONLINE", font=font(13, True), fill=GREEN)
    draw.text((265, ay2 - 40), "HIDZ PROJECT", font=font(13, True), fill=AMBER)

    # Right-side identity.
    rx = 525
    draw.text((rx, 106), "PROFILE / 001", font=font(13, True), fill=CYAN)
    draw.text((rx, 135), NAME, font=font(27, True), fill=WHITE)
    draw.text((rx, 177), ROLE, font=font(12, True), fill=AMBER)
    draw.text((rx, 196), f"github.com/{LOGIN}" if LOGIN else "github.com/your-username", font=font(10, True), fill=MUTED)
    draw.line((rx, 214, 960, 214), fill=LINE, width=1)

    fields = [
        ("LOCATION", LOCATION),
        ("FOCUS", "WEB DEVELOPMENT • AUTOMATION • SECURITY"),
        ("STACK", "HTML • CSS • JS • PHP • NODE.JS"),
        ("DATABASE", "MYSQL • POSTGRESQL • SQLITE"),
            ]
    y = 228
    for label, value in fields:
        draw.text((rx, y), label, font=font(11, True), fill=MUTED)
        draw_wrapped_text(draw, value, (rx + 118, y - 2), 405, font(13, True), WHITE, 3)
        y += 52

    # Stats cards.
    cards = [
        ("REPOSITORIES", stats["repos"]),
        ("STARS", stats["stars"]),
        ("FOLLOWERS", stats["followers"]),
        ("TOP LANG", stats["languages"]),
    ]
    x = rx
    for i, (label, value) in enumerate(cards):
        bx = x + i * 110
        draw.rounded_rectangle((bx, 408, bx + 100, 470), radius=10, fill=(12, 21, 32), outline=LINE, width=1)
        draw.text((bx + 8, 420), label, font=font(6, True), fill=MUTED)
        draw.text((bx + 8, 443), value, font=font(14, True), fill=CYAN if i != 2 else AMBER)

    # Animated terminal text.
    commands = [
        f"echo \"{NAME}\"",
        "build --clean --fast",
        "git status --short",
        "deploy --production",
    ]
    cmd = commands[(frame // 12) % len(commands)]
    progress = frame % 12
    visible = cmd[: min(len(cmd), max(1, progress))]
    terminal_y = 493
    draw.rounded_rectangle((525, terminal_y, 960, 540), radius=10, fill=(6, 11, 17), outline=LINE, width=1)
    draw.text((543, terminal_y + 10), "$", font=font(15, True), fill=AMBER)
    draw.text((565, terminal_y + 10), visible, font=font(14, True), fill=CYAN)
    if frame % 8 < 5:
        cursor_x = 565 + draw.textlength(visible, font=font(14, True))
        draw.rectangle((cursor_x + 3, terminal_y + 11, cursor_x + 10, terminal_y + 27), fill=CYAN)

    draw.text((525, 552), f"{BRAND}  //  OPEN SOURCE  //  PROFILE SYNC", font=font(10, True), fill=MUTED)
    return im


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    stats = fetch_stats()
    avatar = load_avatar()
    frames = [render_frame(i, avatar, stats).convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for i in range(FRAMES)]
    frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()
