#!/usr/bin/env python3
"""Generate platform icons from res/icon.png.

Run from repo root:
  python3 scripts/update_icons_from_png.py

On macOS this also writes flutter/macos/Runner/AppIcon.icns (RustDesk uses
AppIcon.icns directly, not Assets.xcassets, so flutter_launcher_icons skips macOS).

Optional: cd flutter && dart run flutter_launcher_icons  (Android/iOS/Windows)
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: pip install Pillow")
    raise

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "res" / "icon.png"
# Multiple sizes so OS picks nearest (reduces blur from scaling); include 128 for desktop/taskbar
SIZES_ICO = (16, 24, 32, 48, 64, 128, 256)


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


def fit_symbol_to_square(
    img: Image.Image,
    size: int = 512,
    *,
    padding: float = 0.08,
) -> Image.Image:
    """Scale a wide logo into a square canvas without stretching (letterbox)."""
    img = _make_bg_transparent(img)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    inner = int(size * (1 - 2 * padding))
    img.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    return canvas


def write_square_icon_from_symbol(symbol_path: Path, *destinations: Path, size: int = 512) -> Image.Image:
    symbol_path = symbol_path.resolve()
    if not symbol_path.exists():
        raise FileNotFoundError(f"Symbol source not found: {symbol_path}")
    icon = fit_symbol_to_square(Image.open(symbol_path), size=size)
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        icon.save(destination)
    return icon


def generate_macos_icns(source: Path, output: Path) -> None:
    """Build AppIcon.icns with sips/iconutil (macOS only)."""
    if shutil.which("iconutil") is None or shutil.which("sips") is None:
        print("iconutil/sips not found; skip macOS AppIcon.icns")
        return
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"macOS icon source not found: {source}")
    iconset_entries = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]
    with tempfile.TemporaryDirectory(prefix="multidesk-iconset-") as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()
        for name, size in iconset_entries:
            dest = iconset / name
            subprocess.run(
                ["sips", "-z", str(size), str(size), str(source), "--out", str(dest)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(output.resolve())],
            check=True,
        )
    print(f"Wrote {output}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate MultiDesk icons from res/icon.png")
    parser.add_argument(
        "--from-symbol",
        type=Path,
        help="Build square res/icon.png from a wide symbol PNG (preserves aspect ratio)",
    )
    args = parser.parse_args()

    if args.from_symbol:
        write_square_icon_from_symbol(
            args.from_symbol,
            REPO_ROOT / "res" / "icon.png",
            REPO_ROOT / "res" / "mac-icon.png",
        )
        print(f"Wrote square icons from {args.from_symbol}")

    if not SRC.exists():
        print(f"Source not found: {SRC}")
        return 1
    img = Image.open(SRC).convert("RGBA")
    img = _make_bg_transparent(img)
    # Build multi-size ico (Pillow requires saving from the largest image first).
    icons = [img.resize((size, size), Image.Resampling.LANCZOS) for size in SIZES_ICO]
    ico_sizes = [(s, s) for s in SIZES_ICO]

    def write_ico(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        icons[-1].save(
            path,
            format="ICO",
            sizes=ico_sizes,
            append_images=icons[:-1],
        )

    # Windows runner icon
    out_win = REPO_ROOT / "flutter" / "windows" / "runner" / "resources" / "app_icon.ico"
    write_ico(out_win)
    print(f"Wrote {out_win}")
    # res/icon.ico + runtime copy for win32_window LoadCustomIcon()
    out_res = REPO_ROOT / "res" / "icon.ico"
    write_ico(out_res)
    print(f"Wrote {out_res}")
    out_flutter_ico = REPO_ROOT / "flutter" / "assets" / "icon.ico"
    write_ico(out_flutter_ico)
    print(f"Wrote {out_flutter_ico}")
    # Tray icon: include 16 and 32 so taskbar picks sharp size
    out_tray = REPO_ROOT / "res" / "tray-icon.ico"
    t16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    t32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    t32.save(out_tray, format="ICO", sizes=[(16, 16), (32, 32)], append_images=[t16])
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

    mac_src = REPO_ROOT / "res" / "mac-icon.png"
    mac_icns = REPO_ROOT / "flutter" / "macos" / "Runner" / "AppIcon.icns"
    generate_macos_icns(mac_src, mac_icns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
