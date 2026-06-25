"""Greenlight screenshot engine (Pillow reference implementation).

This is the fallback renderer. The production path (see BUILD_PROMPT.md) moves
templates to HTML/CSS rendered headless with Playwright so the cockpit and the
renderer share one template and hot-reload like HyperFrames.

Design follows docs/DESIGN_CORE.md: single accent (Greenlight green), warm
near-black surface, no purple gradient, no glassmorphism, no emoji.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Exact store asset spec sizes, 2026. Verify against the official spec pages.
SPECS = {
    "iphone_6_9":   {"w": 1320, "h": 2868, "store": "App Store", "note": "iPhone 6.9 inch, primary required"},
    "iphone_6_5":   {"w": 1242, "h": 2688, "store": "App Store", "note": "iPhone 6.5 inch, legacy"},
    "ipad_13":      {"w": 2064, "h": 2752, "store": "App Store", "note": "iPad 13 inch"},
    "play_phone":   {"w": 1080, "h": 1920, "store": "Google Play", "note": "phone screenshot"},
    "play_feature": {"w": 1024, "h": 500,  "store": "Google Play", "note": "feature graphic, no alpha"},
}

INK_BG = (22, 21, 19)      # warm near-black surface
OFFWHITE = (244, 239, 230)
MUTED = (150, 148, 142)
ACCENT = (38, 197, 126)    # Greenlight green, the single accent

_FONT_CANDIDATES = [
    str(Path.home() / "Library/Fonts/Pretendard-Bold.otf"),
    str(Path.home() / "Library/Fonts/PretendardVariable.ttf"),
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _grain(w: int, h: int, opacity: int = 10) -> Image.Image:
    import random
    n = Image.new("L", (w // 3, h // 3))
    n.putdata([random.randint(0, opacity) for _ in range((w // 3) * (h // 3))])
    return n.resize((w, h)).convert("L")


def _center(d: ImageDraw.ImageDraw, cx: int, y: int, text: str,
            font: ImageFont.FreeTypeFont, fill, stroke: int = 0) -> int:
    bb = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), text, font=font, fill=fill,
           stroke_width=stroke, stroke_fill=fill)
    return bb[3] - bb[1]


def render_marketing_panel(spec: str, headline: str, subtitle: str,
                           out_path: str | Path, screen_img: str | None = None) -> Path:
    """Render one store screenshot at the given spec size and save a PNG."""
    if spec not in SPECS:
        raise ValueError(f"unknown spec '{spec}'. options: {list(SPECS)}")
    w, h = SPECS[spec]["w"], SPECS[spec]["h"]
    img = Image.new("RGB", (w, h), INK_BG)
    img.paste((30, 28, 25), (0, 0, w, h), _grain(w, h, 14))
    d = ImageDraw.Draw(img)

    pad = int(w * 0.085)
    y = int(h * 0.10)
    for line in headline.split("\n"):
        y += _center(d, w // 2, y, line, _font(int(w * 0.115)), OFFWHITE, stroke=2) + int(h * 0.012)
    # single accent: a short green rule under the headline block (the signature)
    d.rounded_rectangle([w // 2 - int(w * 0.06), y + int(h * 0.005),
                         w // 2 + int(w * 0.06), y + int(h * 0.005) + max(6, w // 150)],
                        radius=max(3, w // 300), fill=ACCENT)
    if subtitle:
        _center(d, w // 2, y + int(h * 0.03), subtitle, _font(int(w * 0.042)), MUTED)

    # device frame with a real-screen slot
    dw = int(w * 0.70); dx = (w - dw) // 2; dy = int(h * 0.40); dh = int(dw * 2.05)
    d.rounded_rectangle([dx - 6, dy - 6, dx + dw + 6, dy + dh + 6], radius=120, fill=(10, 10, 12))
    d.rounded_rectangle([dx, dy, dx + dw, dy + dh], radius=112, fill=(8, 8, 10))
    sx0, sy0, sx1, sy1 = dx + 20, dy + 20, dx + dw - 20, dy + dh - 20
    if screen_img and Path(screen_img).exists():
        cap = Image.open(screen_img).convert("RGB").resize((sx1 - sx0, sy1 - sy0))
        mask = Image.new("L", cap.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, cap.size[0], cap.size[1]], radius=96, fill=255)
        img.paste(cap, (sx0, sy0), mask)
    else:
        d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=96, fill=(16, 16, 18))
        _center(d, (sx0 + sx1) // 2, (sy0 + sy1) // 2,
                "real app screen", _font(int(w * 0.034)), MUTED)
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    return out


def render_feature_graphic(headline: str, subtitle: str, out_path: str | Path) -> Path:
    """Render a Google Play feature graphic (1024x500, no alpha)."""
    w, h = SPECS["play_feature"]["w"], SPECS["play_feature"]["h"]
    img = Image.new("RGB", (w, h), INK_BG)
    img.paste((30, 28, 25), (0, 0, w, h), _grain(w, h, 14))
    d = ImageDraw.Draw(img)
    d.text((70, 150), headline, font=_font(72), fill=OFFWHITE)
    d.rectangle([72, 250, 72 + 120, 250 + 8], fill=ACCENT)
    d.text((72, 280), subtitle, font=_font(34), fill=MUTED)
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    return out


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[2] / "renders"
    print(render_marketing_panel("iphone_6_9", "Pass review\non the first try",
                                 "Audit, screenshots, and submission in one place",
                                 base / "sample_iphone_6_9.png"))
    print(render_feature_graphic("Greenlight", "Ship to the App Store and Google Play",
                                 base / "sample_play_feature.png"))
