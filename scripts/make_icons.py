"""
Generate placeholder icon files for packaging.

Mirrors the runtime tray-icon look (purple disc + bold "T") from
app.main_window._make_tray_icon and writes:

    assets/icon.png   — 256×256 PNG (Linux .desktop / AppImage)
    assets/icon.ico   — Windows multi-resolution ICO (16, 32, 48, 64, 128, 256)

Run before any build:

    python scripts/make_icons.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.stderr.write(
        "Pillow is required: pip install -r requirements-dev.txt\n"
    )
    sys.exit(1)


# Matches styles.C["accent"]
ACCENT  = (91, 106, 240, 255)   # #5B6AF0
WHITE   = (255, 255, 255, 255)
TRANSP  = (0, 0, 0, 0)

REPO_ROOT  = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"


def _pick_bold_font(size: int) -> ImageFont.ImageFont:
    """
    Try a few common bold fonts; fall back to PIL default if none exist.
    The icon stays legible at 16×16 because the glyph is the only feature.
    """
    candidates = [
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def render(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), TRANSP)
    draw = ImageDraw.Draw(img)

    pad = max(1, size // 16)
    draw.ellipse((pad, pad, size - pad, size - pad), fill=ACCENT)

    glyph_size = int(size * 0.6)
    font = _pick_bold_font(glyph_size)
    bbox = draw.textbbox((0, 0), "T", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # textbbox returns offsets from origin including negative space; account
    # for that to actually center the glyph inside the disc.
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "T", fill=WHITE, font=font)

    return img


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    png_path = ASSETS_DIR / "icon.png"
    ico_path = ASSETS_DIR / "icon.ico"

    render(256).save(png_path, format="PNG")
    print(f"wrote {png_path.relative_to(REPO_ROOT)}")

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base = render(256)
    base.save(ico_path, format="ICO", sizes=sizes)
    print(f"wrote {ico_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
