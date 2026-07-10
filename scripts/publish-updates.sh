#!/usr/bin/env bash
#
# publish-updates.sh
#
# Download the latest successful MultiDesk build artifacts from GitHub Actions
# and publish them to the self-hosted download page, then bump the update
# manifest (version.json) so clients auto-update.
#
# Requirements: `gh` authenticated with repo+workflow scope (gh auth status),
# and write access to the downloads directory.
#
# Usage:
#   scripts/publish-updates.sh                # publish windows, android, macos
#   scripts/publish-updates.sh windows        # only specific platforms
#   scripts/publish-updates.sh android macos
#
# Notes:
#   * macOS is published as the arm64 (Apple Silicon) build.
#   * The manifest uses a single version for all platforms; this script only
#     bumps it once the requested platforms are downloaded successfully.

set -euo pipefail

REPO="kenmckenzie/multidesk"
BASE_URL="https://multidesk.multisaas.co.za/download"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DL="$ROOT/rustdesk-api-docker/downloads"
MANIFEST="$DL/version.json"
INDEX="$DL/index.html"

# Platforms to publish.
PLATFORMS=("$@")
if [ ${#PLATFORMS[@]} -eq 0 ]; then
  PLATFORMS=(windows android macos linux)
fi
want() { printf '%s\n' "${PLATFORMS[@]}" | grep -qx "$1"; }

command -v gh >/dev/null || { echo "error: gh CLI not found" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "error: gh not authenticated (run: gh auth login)" >&2; exit 1; }
[ -d "$DL" ] || { echo "error: downloads dir not found: $DL" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

latest_success() {
  gh run list -R "$REPO" --workflow="$1" --status success --limit 1 \
    --json databaseId --jq '.[0].databaseId // empty'
}

VERSION=""
set_version() {
  if [ -z "$VERSION" ]; then
    VERSION="$1"
  elif [ "$VERSION" != "$1" ]; then
    echo "warning: version mismatch across platforms ($VERSION vs $1)" >&2
  fi
}

if want windows; then
  echo ">> Windows: locating latest successful build..."
  run="$(latest_success multidesk-windows.yml)"
  [ -n "$run" ] || { echo "error: no successful Windows run" >&2; exit 1; }
  gh run download "$run" -R "$REPO" -n multidesk-windows-installer -D "$TMP/win"
  exe="$(ls "$TMP/win"/multidesk-*-install.exe 2>/dev/null | head -1)"
  [ -n "$exe" ] || { echo "error: installer exe not found in artifact" >&2; exit 1; }
  set_version "$(basename "$exe" | sed -E 's/^multidesk-(.+)-install\.exe$/\1/')"
  rm -f "$DL/multidesk-install.exe"
  cp -f "$exe" "$DL/multidesk-install.exe"
  echo "   published multidesk-install.exe (run $run)"
fi

if want android; then
  echo ">> Android: locating latest successful build..."
  run="$(latest_success multidesk-android.yml)"
  [ -n "$run" ] || { echo "error: no successful Android run" >&2; exit 1; }
  gh run download "$run" -R "$REPO" -n multidesk-android-aarch64-release -D "$TMP/apk"
  apk="$(ls "$TMP/apk"/*.apk 2>/dev/null | head -1)"
  [ -n "$apk" ] || { echo "error: apk not found in artifact" >&2; exit 1; }
  # Prefer the version embedded in the artifact filename when present.
  aver="$(basename "$apk" | sed -nE 's/^multidesk-([0-9.]+)-.*\.apk$/\1/p')"
  [ -n "$aver" ] && set_version "$aver"
  ANDROID_APK="multidesk-${VERSION}-aarch64-release.apk"
  # Remove stale versioned apks, then publish the new one.
  find "$DL" -maxdepth 1 -name 'multidesk-*-aarch64-release.apk' -delete
  cp -f "$apk" "$DL/$ANDROID_APK"
  echo "   published $ANDROID_APK (run $run)"
fi

if want macos; then
  echo ">> macOS (arm64): locating latest run with the aarch64 artifact..."
  # The macOS run can be marked "failure" if the x86_64 leg fails while arm64
  # still produced its artifact, so search recent runs for the artifact.
  run=""
  for rid in $(gh run list -R "$REPO" --workflow=multidesk-macos.yml --limit 10 \
                 --json databaseId --jq '.[].databaseId'); do
    if gh api "repos/$REPO/actions/runs/$rid/artifacts" \
         --jq '.artifacts[].name' 2>/dev/null | grep -qx multidesk-macos-aarch64; then
      run="$rid"; break
    fi
  done
  [ -n "$run" ] || { echo "error: no macOS run with an aarch64 artifact" >&2; exit 1; }
  gh run download "$run" -R "$REPO" -n multidesk-macos-aarch64 -D "$TMP/mac"
  zip="$(ls "$TMP/mac"/MultiDesk-*-aarch64.zip 2>/dev/null | head -1)"
  [ -n "$zip" ] || { echo "error: macOS zip not found in artifact" >&2; exit 1; }
  mver="$(basename "$zip" | sed -nE 's/^MultiDesk-([0-9.]+)-aarch64\.zip$/\1/p')"
  [ -n "$mver" ] && set_version "$mver"
  rm -f "$DL/MultiDesk.app.zip"
  cp -f "$zip" "$DL/MultiDesk.app.zip"
  echo "   published MultiDesk.app.zip (run $run)"
fi

if want linux; then
  echo ">> Linux (x86_64): locating latest successful build..."
  run="$(latest_success multidesk-linux.yml)"
  [ -n "$run" ] || { echo "error: no successful Linux run" >&2; exit 1; }
  gh run download "$run" -R "$REPO" -n multidesk-linux-x86_64 -D "$TMP/linux"
  appimage="$(ls "$TMP/linux"/MultiDesk-*-linux-x86_64.AppImage 2>/dev/null | head -1)"
  deb="$(ls "$TMP/linux"/MultiDesk-*-linux-amd64.deb 2>/dev/null | head -1)"
  rpm="$(ls "$TMP/linux"/MultiDesk-*-linux-x86_64.rpm 2>/dev/null | head -1)"
  targz="$(ls "$TMP/linux"/MultiDesk-*-linux-x86_64.tar.gz 2>/dev/null | head -1)"
  [ -n "$appimage" ] && [ -n "$deb" ] || { echo "error: AppImage/.deb not found in artifact" >&2; exit 1; }
  lver="$(basename "$appimage" | sed -nE 's/^MultiDesk-([0-9.]+)-linux-x86_64\.AppImage$/\1/p')"
  [ -n "$lver" ] && set_version "$lver"
  # Remove stale versioned Linux files, then publish the new ones.
  find "$DL" -maxdepth 1 \( -name 'MultiDesk-*-linux-x86_64.AppImage' \
    -o -name 'MultiDesk-*-linux-amd64.deb' \
    -o -name 'MultiDesk-*-linux-x86_64.rpm' \
    -o -name 'MultiDesk-*-linux-x86_64.tar.gz' \) -delete
  cp -f "$appimage" "$DL/MultiDesk-${VERSION}-linux-x86_64.AppImage"
  cp -f "$deb" "$DL/MultiDesk-${VERSION}-linux-amd64.deb"
  [ -n "$rpm" ] && cp -f "$rpm" "$DL/MultiDesk-${VERSION}-linux-x86_64.rpm"
  [ -n "$targz" ] && cp -f "$targz" "$DL/MultiDesk-${VERSION}-linux-x86_64.tar.gz"
  echo "   published Linux AppImage/.deb${rpm:+/.rpm}${targz:+/.tar.gz} (run $run)"
fi

[ -n "$VERSION" ] || { echo "error: could not determine version" >&2; exit 1; }
echo ">> Detected version: $VERSION"

# --- Update the manifest (version.json) ---
if [ -f "$MANIFEST" ]; then
  ANDROID_URL="$BASE_URL/multidesk-${VERSION}-aarch64-release.apk"
  python3 - "$MANIFEST" "$VERSION" "$ANDROID_URL" <<'PY'
import json, sys
path, version, android_url = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path) as f:
    m = json.load(f)
m["version"] = version
m["android"] = android_url
with open(path, "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
print(f"   version.json -> {version}")
PY
fi

# --- Update the download page's versioned links ---
if [ -f "$INDEX" ]; then
  sed -i -E "s#href=\"multidesk-[0-9.]+-aarch64-release\.apk\"#href=\"multidesk-${VERSION}-aarch64-release.apk\"#g" "$INDEX"
  sed -i -E "s#href=\"MultiDesk-[0-9.]+-linux-x86_64\.AppImage\"#href=\"MultiDesk-${VERSION}-linux-x86_64.AppImage\"#g" "$INDEX"
  sed -i -E "s#href=\"MultiDesk-[0-9.]+-linux-amd64\.deb\"#href=\"MultiDesk-${VERSION}-linux-amd64.deb\"#g" "$INDEX"
  sed -i -E "s#href=\"MultiDesk-[0-9.]+-linux-x86_64\.rpm\"#href=\"MultiDesk-${VERSION}-linux-x86_64.rpm\"#g" "$INDEX"
  sed -i -E "s#href=\"MultiDesk-[0-9.]+-linux-x86_64\.tar\.gz\"#href=\"MultiDesk-${VERSION}-linux-x86_64.tar.gz\"#g" "$INDEX"
  echo "   index.html versioned links -> $VERSION"
fi

echo ">> Done. Verifying served files..."
for f in multidesk-install.exe "multidesk-${VERSION}-aarch64-release.apk" MultiDesk.app.zip \
         "MultiDesk-${VERSION}-linux-x86_64.AppImage" "MultiDesk-${VERSION}-linux-amd64.deb" \
         "MultiDesk-${VERSION}-linux-x86_64.rpm" "MultiDesk-${VERSION}-linux-x86_64.tar.gz" version.json; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 -I "$BASE_URL/$f" || echo 000)"
  echo "   $code  $f"
done
echo ">> Published MultiDesk $VERSION."
