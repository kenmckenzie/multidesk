# MultiDesk Custom Build Instructions

This document describes how to build a custom Windows executable named "MultiDesk" with pre-configured server settings.

## Configuration

The MultiDesk build includes the following default configuration:
- **ID Server**: multidesk.multisaas.co.za
- **Relay Server**: multidesk.multisaas.co.za
- **API Server**: (blank)
- **Key**: P9AGH4SDGX2F6s3vu+VXIqfxBIYCPlc1HrNGssqwQN8=
- **Application Name**: MultiDesk

## Changes Made

1. **Cargo.toml**: Added a new binary entry for `multidesk` and updated Windows resource metadata
2. **src/common.rs**: Added `set_multidesk_defaults()` function that automatically sets server configuration when the executable name contains "multidesk"
3. **src/main.rs**: Updated CLI app name to use dynamic app name

## Building MultiDesk

### Prerequisites

- Rust development environment
- C++ build tools
- vcpkg installed with required dependencies
- Windows SDK (for Windows builds)

### Build Steps

1. **Build the MultiDesk binary**:
   ```bash
   cargo build --release --bin multidesk
   ```

   The executable will be located at:
   ```
   target/release/multidesk.exe
   ```

2. **For Windows with inline feature** (includes manifest):
   ```bash
   cargo build --release --bin multidesk --features inline
   ```

### Alternative: Filename-based Configuration

You can also use the filename-based configuration approach by renaming the executable:

```
multidesk-host=multidesk.multisaas.co.za,relay=multidesk.multisaas.co.za,key=P9AGH4SDGX2F6s3vu+VXIqfxBIYCPlc1HrNGssqwQN8=.exe
```

This approach works alongside the code-based defaults and will override them if present.

## How It Works

1. When the application starts, `load_custom_client()` is called
2. This function checks if the executable name contains "multidesk" (case-insensitive)
3. If found, it:
   - Sets the application name to "MultiDesk"
   - Sets default server configuration values (only if not already configured)
   - These defaults are applied before any user configuration is loaded

## Verification

After building, verify the configuration:

1. Run the executable
2. Check the application title - it should show "MultiDesk"
3. Go to Settings → ID/Relay Server
4. Verify that the ID Server, Relay Server, and Key fields are pre-filled with the configured values

## Notes

- The defaults are only applied if the configuration fields are empty
- Users can still override these settings through the UI
- The API Server field is intentionally left blank as requested
- The executable name detection is case-insensitive

## GitHub Actions CI

Builds for platforms that cannot be compiled on macOS are available as GitHub Actions workflows.

### Android APK

Workflow: `.github/workflows/multidesk-android.yml`

1. Push this repo to GitHub (or merge the workflow file to `master`).
2. Authenticate the GitHub CLI: `gh auth login`
3. Trigger a build (arm64 phone APK by default):

```bash
gh workflow run "Build MultiDesk (Android)"
```

Optional inputs:

```bash
# All phone/tablet ABIs
gh workflow run "Build MultiDesk (Android)" -f abi=all -f reltype=release

# x86_64 emulator APK
gh workflow run "Build MultiDesk (Android)" -f abi=x86_64 -f reltype=release
```

4. Download the APK from the run’s **Artifacts** tab, or:

```bash
gh run list --workflow="Build MultiDesk (Android)" --limit 1
gh run download <run-id> -D ./apk-out
```

APKs are named `multidesk-<version>-<arch>-release.apk`. Without `ANDROID_SIGNING_*` repository secrets, the workflow uses a debug keystore (fine for testing; not for Play Store).

### Windows

Workflow: `.github/workflows/multidesk-windows.yml`

```bash
gh workflow run "Build MultiDesk (Windows)"
```

Artifacts: `multidesk-windows`, `multidesk-windows-flutter`, and `multidesk-windows-installer`.

### Linux

Workflow: `.github/workflows/multidesk-linux.yml`

```bash
gh workflow run "Build MultiDesk (Linux)"
```

Artifacts: `multidesk-linux-x86_64`, containing an AppImage, a Debian package, and a portable Linux bundle. The Linux runner is named `multidesk`, uses the MultiDesk desktop title/icon, and applies the same default ID/relay configuration as the Windows build.

### Icons (all platforms)

Use one canonical square logo at `res/mac-icon.png` (same look as the macOS dock icon). Regenerate bundle icons with:

```bash
python3 scripts/update_icons_from_png.py
cd flutter && dart run flutter_launcher_icons   # Android + iOS only
```

Windows `app_icon.ico` and macOS `AppIcon.icns` come from the script (not `flutter_launcher_icons`).
