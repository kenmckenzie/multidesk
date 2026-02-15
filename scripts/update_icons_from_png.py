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
# Multiple sizes so OS picks nearest (reduces blur from scaling)
SIZES_ICO = (16, 24, 32, 48, 64, 256)


def _make_bg_transparent(img: Image.Image, threshold: int = 30) -> Image.Image:
    """Replace black/near-black background with transparency. Preserves logo color."""
    img = img.convert("RGBA")
    data = img.getdata()
    out = []
    for item in data:
        r, g, b, a = item
        if r <= threshold and g <= threshold and b <= threshold:
            out.append((r, g, b, 0))
        else:
            out.append(item)
    img.putdata(out)
    return img


def main():
    if not SRC.exists():
        print(f"Source not found: {SRC}")
        return 1
    img = Image.open(SRC).convert("RGBA")
    img = _make_bg_transparent(img)
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
    # Tray icon: include 16 and 32 so taskbar picks sharp size
    out_tray = REPO_ROOT / "res" / "tray-icon.ico"
    t16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    t32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    t16.save(out_tray, format="ICO", sizes=[(16, 16), (32, 32)], append_images=[t32])
    print(f"Wrote {out_tray}")
    # In-app icon: transparent PNG for loadIcon() (no black background)
    out_app_icon = REPO_ROOT / "flutter" / "assets" / "icon.png"
    out_app_icon.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_app_icon)
    print(f"Wrote {out_app_icon}")

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
