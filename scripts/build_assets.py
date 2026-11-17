"""
Builds the optimised images used by the site from the originals in source/.

    python scripts/build_assets.py

What it does
  1. Resizes the photos in source/images/ to WebP files in public/images/
     (several widths each, so phones download small files).
  2. Draws the favicon and app icons (public/favicon.ico, apple-touch-icon.png,
     icon-192.png, icon-512.png).
  3. Renders source/og-image.html with headless Chrome/Edge to
     public/og-image.jpg (the 1200x630 social sharing preview).

Requires: Python 3.9+ and Pillow (pip install Pillow).
Step 3 also needs Google Chrome or Microsoft Edge installed; it is skipped
with a warning if neither is found.

To swap a photo: replace the file in source/images/ (keep the same name and
roughly the same shape), then run this script again.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "images"
OUT = ROOT / "public" / "images"
PUBLIC = ROOT / "public"

# name -> (aspect ratio w/h, vertical focus 0..1, output widths)
IMAGES = {
    "kokil-hero":         (4 / 5, 0.35, [480, 720, 960]),
    "kokil-about":        (1 / 1, 0.40, [460, 690, 920]),
    "work-code-and-debug": (4 / 3, 0.50, [600, 900, 1200]),
    "work-baker-assist":   (4 / 3, 0.50, [600, 900, 1200]),
    "work-nehal-smart-qr": (4 / 3, 0.50, [600, 900, 1200]),
}


def crop_to_ratio(im: Image.Image, ratio: float, focus_y: float) -> Image.Image:
    w, h = im.size
    if w / h > ratio:  # too wide: trim the sides evenly
        nw = round(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = round(w / ratio)  # too tall: trim top/bottom around the focus point
    top = int(max(0, min(h - nh, focus_y * h - nh / 2)))
    return im.crop((0, top, w, top + nh))


def build_photos() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (ratio, focus, widths) in IMAGES.items():
        src = SRC / f"{name}.png"
        if not src.exists():
            print(f"  ! missing {src.relative_to(ROOT)}, skipped")
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = crop_to_ratio(im, ratio, focus)
        for w in widths:
            if w > im.width:
                print(f"  ! {name}: source is only {im.width}px wide, skipping {w}w")
                continue
            h = round(w / ratio)
            out = OUT / f"{name}-{w}.webp"
            im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=80, method=6)
            print(f"  {out.relative_to(ROOT)}  {w}x{h}  {out.stat().st_size // 1024} KB")


def build_icons(browser: str) -> None:
    """The 'KS' monogram (source/icon.html) at every size browsers ask for."""
    im = screenshot(browser, ROOT / "source" / "icon.html", 512, 512)
    im.save(PUBLIC / "icon-512.png", optimize=True)
    im.resize((192, 192), Image.LANCZOS).save(PUBLIC / "icon-192.png", optimize=True)
    im.resize((180, 180), Image.LANCZOS).save(PUBLIC / "apple-touch-icon.png", optimize=True)
    im.resize((48, 48), Image.LANCZOS).save(
        PUBLIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print("  public/favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png")


def find_browser() -> str | None:
    candidates = [
        os.environ.get("CHROME_PATH", ""),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def screenshot(browser: str, page: Path, width: int, height: int) -> Image.Image:
    """Render a local HTML file with headless Chrome/Edge and return the image."""
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "shot.png"
        subprocess.run(
            [
                browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--allow-file-access-from-files", "--force-device-scale-factor=1",
                f"--window-size={width},{height}", "--virtual-time-budget=4000",
                f"--user-data-dir={tmp}", f"--screenshot={shot}", page.as_uri(),
            ],
            check=True, capture_output=True, timeout=60,
        )
        im = Image.open(shot).convert("RGB")
        im.load()
    if im.size != (width, height):
        im = ImageOps.fit(im, (width, height), Image.LANCZOS, centering=(0, 0))
    return im


def build_og_image(browser: str) -> None:
    im = screenshot(browser, ROOT / "source" / "og-image.html", 1200, 630)
    out = PUBLIC / "og-image.jpg"
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"  {out.relative_to(ROOT)}  1200x630  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    print("Photos:")
    build_photos()
    browser = find_browser()
    if not browser:
        print("! Chrome/Edge not found: icons and og-image.jpg not rebuilt (set CHROME_PATH)")
        sys.exit(0)
    print("Icons:")
    build_icons(browser)
    print("Social preview:")
    build_og_image(browser)
