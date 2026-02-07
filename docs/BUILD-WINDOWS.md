# Windows build: Sciter vs Flutter

Official **RustDesk** Windows 64-bit builds use the **Flutter** UI (modern interface in `flutter/`).  
MultiDesk’s Windows CI builds **both** UIs; the difference in look comes from **which UI stack** is built, not from an old codebase.

| Artifact | UI | Contents |
|----------|----|----------|
| **multidesk-windows** | Sciter (legacy) | `multidesk.exe` + `sciter.dll` — older look |
| **multidesk-windows-flutter** | Flutter | Same look as current RustDesk — `rustdesk.exe` + Flutter runtime DLLs |

- **CI:** On push to `master`, the `Build MultiDesk (Windows)` workflow runs:
  - **build-windows** → Sciter build → artifact `multidesk-windows`
  - **build-windows-flutter** → Flutter build (after bridge generation) → artifact `multidesk-windows-flutter`
- **Local Flutter build:**  
  Generate the bridge, then `python build.py --flutter --hwcodec --skip-portable-pack`.  
  See RustDesk’s [flutter-build.yml](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml) for full CI steps (custom engine, vcpkg, etc.).
