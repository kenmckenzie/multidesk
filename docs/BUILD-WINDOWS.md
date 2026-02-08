# Windows build: Sciter vs Flutter

Official **RustDesk** Windows 64-bit builds use the **Flutter** UI (modern interface in `flutter/`).  
MultiDesk’s Windows CI builds **both** UIs.

| Artifact | UI | Contents | DLLs / footprint |
|----------|----|----------|------------------|
| **multidesk-windows** | Sciter (legacy) | `multidesk.exe` + `sciter.dll` | **Minimal** — only 2 files. Use this if you want the smallest deployment. |
| **multidesk-windows-flutter** | Flutter | `multidesk.exe` + Flutter engine DLLs | Same as RustDesk — many DLLs (flutter_windows.dll, VC++ runtime, etc.). Required for the modern UI. |

- **Branding and ID/relay:** The Flutter artifact is built as `rustdesk.exe` then **renamed to `multidesk.exe`** in CI. When the executable name contains `multidesk`, the app applies MultiDesk branding and default ID/relay/API server (see `src/common.rs`).
- **CI:** On push to `master`:
  - **build-windows** → Sciter → artifact `multidesk-windows` (2 files).
  - **build-windows-flutter** → Flutter + hwcodec → artifact `multidesk-windows-flutter` (multidesk.exe + DLLs).
- **Fewer DLLs:** To avoid the Flutter runtime DLL set, use the **Sciter** artifact (`multidesk-windows`). For the modern UI you need the Flutter build and its DLLs; RustDesk ships the same way.
- **`uni_links_desktop_plugin.dll` not found:** The Flutter build and CI now ensure this plugin DLL is copied into the Release folder (and thus into the artifact or installer). If you still see the error, ensure you use the latest build; the DLL must sit next to `multidesk.exe`.
