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
