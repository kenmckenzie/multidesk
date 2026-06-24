#!/usr/bin/env bash
set -euo pipefail

# Apply RustDesk's DropdownMenu enableFilter fix to Flutter 3.24.5.
# Idempotent: cached Flutter SDKs may already have the patch applied.

FLUTTER_VERSION="${FLUTTER_VERSION:-3.24.5}"
PATCH_NAME="flutter_3.24.4_dropdown_menu_enableFilter.diff"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_SRC="${SCRIPT_DIR}/${PATCH_NAME}"

if [[ "${FLUTTER_VERSION}" != "3.24.5" ]]; then
  echo "Skipping Flutter dropdown patch (version ${FLUTTER_VERSION})"
  exit 0
fi

FLUTTER_ROOT="${FLUTTER_ROOT:-$(dirname "$(dirname "$(which flutter)")")}"
cd "${FLUTTER_ROOT}"
cp "${PATCH_SRC}" .

if git apply --reverse --check "${PATCH_NAME}" 2>/dev/null; then
  echo "Flutter dropdown patch already applied, skipping"
elif git apply "${PATCH_NAME}"; then
  echo "Flutter dropdown patch applied"
else
  echo "Failed to apply Flutter dropdown patch"
  exit 1
fi
