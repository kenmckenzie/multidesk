# White Labeling Options for MultiDesk

This document outlines all available white labeling and customization options for MultiDesk.

## Application Branding

### 1. Application Name
**Location:** `Cargo.toml`
```toml
[package.metadata.winres]
ProductName = "MultiDesk"
FileDescription = "MultiDesk Remote Desktop"
OriginalFilename = "multidesk.exe"
```

**What it affects:**
- Windows executable properties
- Window title bar
- Task manager display name
- About dialog

### 2. Copyright Information
**Location:** `Cargo.toml`
```toml
LegalCopyright = "Copyright © 2025 MultiSaaS Business Systems (Pty) Ltd. All rights reserved."
```

**What it affects:**
- Windows executable properties
- About dialog (already customized)

## Builtin Options (via Configuration)

These options can be set via builtin configuration to control UI and behavior:

### UI Visibility Options

1. **`hide-powered-by-me`** - Hide "Powered by RustDesk" text
   - Set to `"Y"` to hide
   - Location: `src/ui/index.tis` line 705

2. **`hide-server-settings`** - Hide ID/Relay Server settings
   - Set to `"Y"` to hide
   - Prevents users from changing server configuration

3. **`hide-proxy-settings`** - Hide Socks5/Http(s) Proxy settings
   - Set to `"Y"` to hide
   - Prevents users from configuring proxy

4. **`hide-websocket-settings`** - Hide WebSocket settings
   - Set to `"Y"` to hide
   - Prevents users from enabling WebSocket

### Feature Disable Options

5. **`disable-settings`** - Disable all settings menu
   - Set to `"Y"` to disable
   - Hides the entire settings menu

6. **`disable-account`** - Disable account/login features
   - Set to `"Y"` to disable
   - Hides login/logout options

7. **`disable-installation`** - Disable installation prompts
   - Set to `"Y"` to disable
   - Hides installation prompts

8. **`disable-ab`** - Disable address book
   - Set to `"Y"` to disable
   - Hides address book features

9. **`disable-change-permanent-password`** - Prevent password changes
   - Set to `"Y"` to disable
   - Users cannot change permanent password

10. **`disable-change-id`** - Prevent ID changes
    - Set to `"Y"` to disable
    - Users cannot change their ID

### Security/Behavior Options

11. **`one-way-file-transfer`** - One-way file transfer only
    - Set to `"Y"` to enable
    - Prevents remote from sending files to local

12. **`one-way-clipboard-redirection`** - One-way clipboard only
    - Set to `"Y"` to enable
    - Prevents remote from reading local clipboard

13. **`preset-username`** - Pre-set username for auto-login
    - Set to username string
    - Auto-fills login form

14. **`preset-strategy-name`** - Pre-set strategy name
    - Set to strategy string
    - For enterprise deployments

15. **`preset-device-group-name`** - Pre-set device group
    - Set to group name string
    - For device grouping

16. **`hide-tray`** - Hide system tray icon
    - Set to `"Y"` to hide
    - Hides tray icon on Windows/Linux

## Custom Client Configuration

RustDesk supports a custom client configuration system that allows:
- Encrypted configuration via signed JSON
- App name customization
- Default settings
- Override settings (hard-coded, cannot be changed)

**Location:** `src/common.rs` - `read_custom_client()`

**Configuration format:**
```json
{
  "app-name": "MultiDesk",
  "default-settings": {
    "allow-darktheme": "Y",
    "enable-keyboard": "Y"
  },
  "override-settings": {
    "hide-server-settings": "Y",
    "disable-change-id": "Y"
  }
}
```

## Default Values for Custom Clients

When `is_custom_client()` returns true (app name != "RustDesk"), defaults change:

- **Language:** `'default'` instead of `''`
- **Theme:** `'system'` instead of `''`
- **Yes/No options:** `'Y'`/`'N'` instead of `''`
- **Whitelist:** `','` instead of `''`
- **Access mode:** `'custom'` instead of `''`
- **Approve mode:** `'password-click'` instead of `''`

## UI Customization

### About Dialog
**Location:** `src/ui/index.tis` line 587-602

Currently customized to show:
- MultiSaaS Business Systems copyright
- Custom license information
- Version and fingerprint

### Logo/Icon
**Location:** `flutter/assets/`
- Replace `logo.png` for main logo
- Replace `icon.png`/`icon.svg` for app icon

### Colors/Themes
**Location:** `src/ui/common.css`, `src/ui/index.css`
- Modify CSS variables for colors
- Dark theme already enabled by default

## Implementation Examples

### Example 1: Hide All Server Settings
Set in configuration:
```rust
BUILTIN_SETTINGS.insert("hide-server-settings", "Y");
BUILTIN_SETTINGS.insert("hide-proxy-settings", "Y");
BUILTIN_SETTINGS.insert("hide-websocket-settings", "Y");
```

### Example 2: Lock Down Settings
Set in configuration:
```rust
BUILTIN_SETTINGS.insert("disable-settings", "Y");
BUILTIN_SETTINGS.insert("disable-change-id", "Y");
BUILTIN_SETTINGS.insert("disable-change-permanent-password", "Y");
```

### Example 3: Hide Branding
Set in configuration:
```rust
BUILTIN_SETTINGS.insert("hide-powered-by-me", "Y");
```

## Where to Set Builtin Options

Builtin options can be set in several ways:

1. **At compile time** - Modify `libs/hbb_common/src/config.rs` (if available)
2. **Via custom client config** - Use encrypted JSON configuration
3. **Via environment variables** - Some options can be set via env vars
4. **Via registry/config file** - Windows registry or config files

## Current Customizations

Already implemented in MultiDesk:
- ✅ Product name: "MultiDesk"
- ✅ File description: "MultiDesk Remote Desktop"
- ✅ Copyright: "MultiSaaS Business Systems (Pty) Ltd."
- ✅ About dialog customized
- ✅ Dark mode enabled by default
- ✅ Default password: "@Cwl1234"

## Additional Customization Opportunities

1. **Replace logo assets** in `flutter/assets/`
2. **Modify CSS** for custom colors/branding
3. **Update translations** in `src/lang/` for custom text
4. **Customize window title** in `src/ui.rs` line 87
5. **Modify About dialog** in `src/ui/index.tis` line 587

## Resources

- RustDesk Customization Guide: https://rustdesk.com/docs/en/self-host/client-configuration/
- Custom Client Configuration: See `src/common.rs` `read_custom_client()`
- Builtin Options: See `src/ui/index.tis` for available options
