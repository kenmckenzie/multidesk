#!/usr/bin/env python3
"""Generate platform icons from res/mac-icon.png (same look as macOS AppIcon.icns).

Run from repo root:
  python3 scripts/update_icons_from_png.py

Uses macOS sips/iconutil when available (no Pillow required). Pillow is optional for
--from-symbol letterboxing from a wide logo PNG.

flutter_launcher_icons is not used for Windows/macOS app bundle icons; this script
writes flutter/windows/runner/resources/app_icon.ico and flutter/macos/Runner/AppIcon.icns.
"""
from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DESKTOP_SRC = REPO_ROOT / "res" / "mac-icon.png"
LEGACY_SRC = REPO_ROOT / "res" / "icon.png"
# Windows picks nearest size; include 256 for crisp taskbar/start-menu icons.
SIZES_ICO = (16, 24, 32, 48, 64, 128, 256)
TRAY_ICO_SIZES = (16, 32)


def _have_sips() -> bool:
    return shutil.which("sips") is not None


def _resize_png(source: Path, size: int, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if _have_sips():
        subprocess.run(
            ["sips", "-z", str(size), str(size), str(source), "--out", str(dest)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        return
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "sips not found and Pillow is not installed; run on macOS or pip install Pillow"
        ) from exc
    img = Image.open(source).convert("RGBA")
    img.resize((size, size), Image.Resampling.LANCZOS).save(dest)


def write_ico_from_png_source(source: Path, output: Path, sizes: tuple[int, ...]) -> None:
    """Write a multi-size .ico using PNG payloads (Windows Vista+)."""
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"Icon source not found: {source}")

    png_blobs: list[tuple[int, bytes]] = []
    with tempfile.TemporaryDirectory(prefix="multidesk-ico-") as tmp:
        tmp_path = Path(tmp)
        for size in sizes:
            png_path = tmp_path / f"{size}.png"
            _resize_png(source, size, png_path)
            png_blobs.append((size, png_path.read_bytes()))

    png_blobs.sort(key=lambda item: item[0])
    count = len(png_blobs)
    header = struct.pack("<HHH", 0, 1, count)
    entries = bytearray()
    images = bytearray()
    offset = 6 + 16 * count
    for size, png_bytes in png_blobs:
        width = 0 if size >= 256 else size
        height = width
        entries.extend(
            struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(png_bytes), offset)
        )
        images.extend(png_bytes)
        offset += len(png_bytes)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(header + entries + images)
    print(f"Wrote {output}")


def generate_macos_icns(source: Path, output: Path) -> None:
    """Build AppIcon.icns with sips/iconutil (macOS only)."""
    if shutil.which("iconutil") is None or not _have_sips():
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
            _resize_png(source, size, dest)
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(output.resolve())],
            check=True,
        )
    print(f"Wrote {output}")


def sync_png_copies(source: Path) -> None:
    """Keep square PNG sources and in-app assets identical to the macOS icon."""
    source = source.resolve()
    copies = [
        REPO_ROOT / "res" / "icon.png",
        REPO_ROOT / "res" / "mac-icon.png",
        REPO_ROOT / "flutter" / "assets" / "icon.png",
    ]
    data = source.read_bytes()
    for dest in copies:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"Wrote {dest}")


def write_square_icon_from_symbol(symbol_path: Path, *destinations: Path, size: int = 512):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("--from-symbol requires Pillow: pip install Pillow") from exc

    def _make_bg_transparent(img: Image.Image, threshold: int = 30) -> Image.Image:
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

    symbol_path = symbol_path.resolve()
    if not symbol_path.exists():
        raise FileNotFoundError(f"Symbol source not found: {symbol_path}")
    img = _make_bg_transparent(Image.open(symbol_path))
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    inner = int(size * 0.84)
    img.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(destination)
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate MultiDesk icons (macOS + Windows) from res/mac-icon.png"
    )
    parser.add_argument(
        "--from-symbol",
        type=Path,
        help="Build square mac-icon.png from a wide symbol PNG (requires Pillow)",
    )
    args = parser.parse_args()

    if args.from_symbol:
        write_square_icon_from_symbol(
            args.from_symbol,
            REPO_ROOT / "res" / "icon.png",
            REPO_ROOT / "res" / "mac-icon.png",
        )
        print(f"Wrote square icons from {args.from_symbol}")

    source = DESKTOP_SRC if DESKTOP_SRC.exists() else LEGACY_SRC
    if not source.exists():
        print(f"Source not found: {source}")
        return 1

    sync_png_copies(source)

    write_ico_from_png_source(
        source,
        REPO_ROOT / "flutter" / "windows" / "runner" / "resources" / "app_icon.ico",
        SIZES_ICO,
    )
    write_ico_from_png_source(source, REPO_ROOT / "res" / "icon.ico", SIZES_ICO)
    write_ico_from_png_source(
        source, REPO_ROOT / "flutter" / "assets" / "icon.ico", SIZES_ICO
    )
    write_ico_from_png_source(
        source, REPO_ROOT / "res" / "tray-icon.ico", TRAY_ICO_SIZES
    )

    generate_macos_icns(
        source,
        REPO_ROOT / "flutter" / "macos" / "Runner" / "AppIcon.icns",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
