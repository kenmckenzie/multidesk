#!/usr/bin/env python3
"""Generate .ico and favicon from res/icon.png for Windows and web.
Run from repo root. For full platform icons + web favicon, also run:
  cd flutter && dart run flutter_launcher_icons
"""
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: pip install Pillow")
    raise

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "res" / "icon.png"
SIZES_ICO = (16, 32, 48, 256)


def main():
    if not SRC.exists():
        print(f"Source not found: {SRC}")
        return 1
    img = Image.open(SRC).convert("RGBA")
    # Build multi-size ico
    icons = []
    for size in SIZES_ICO:
        icons.append(img.resize((size, size), Image.Resampling.LANCZOS))
    # Windows runner icon
    out_win = REPO_ROOT / "flutter" / "windows" / "runner" / "resources" / "app_icon.ico"
    out_win.parent.mkdir(parents=True, exist_ok=True)
    icons[0].save(out_win, format="ICO", sizes=[(s, s) for s in SIZES_ICO], append_images=icons[1:])
    print(f"Wrote {out_win}")
    # res/icon.ico
    out_res = REPO_ROOT / "res" / "icon.ico"
    icons[0].save(out_res, format="ICO", sizes=[(s, s) for s in SIZES_ICO], append_images=icons[1:])
    print(f"Wrote {out_res}")
    # Tray icon (small)
    out_tray = REPO_ROOT / "res" / "tray-icon.ico"
    small = img.resize((16, 16), Image.Resampling.LANCZOS)
    small.save(out_tray, format="ICO", sizes=[(16, 16)])
    print(f"Wrote {out_tray}")
    # Favicon 32x32 for web (if web dir exists / not fully ignored in build)
    web_dir = REPO_ROOT / "flutter" / "web"
    if web_dir.exists():
        favicon = web_dir / "favicon.png"
        favicon.parent.mkdir(parents=True, exist_ok=True)
        img.resize((32, 32), Image.Resampling.LANCZOS).save(favicon)
        print(f"Wrote {favicon}")
    else:
        print("flutter/web/ not present; run 'cd flutter && dart run flutter_launcher_icons' to generate web favicon.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
