# Syncing with RustDesk Upstream (Keeping Whitelabel)

MultiDesk is a fork of [RustDesk](https://github.com/rustdesk/rustdesk). This doc describes how to pull in upstream changes while keeping MultiDesk branding and assets.

## One-time setup

1. **Add the upstream remote** (if not already added):
   ```bash
   git remote add upstream https://github.com/rustdesk/rustdesk
   ```

2. **Whitelabel files** are listed in `scripts/whitelabel-files.txt`. These files are restored to *our* version after every merge so upstream doesn’t overwrite branding. Edit that file if you add or change custom assets or config.

## Regular sync (recommended)

From the repo root:

```bash
./scripts/sync_upstream.sh
```

This script:

1. Fetches `upstream` (RustDesk).
2. Merges `upstream/master` into your current branch **without** committing.
3. Restores every path in `scripts/whitelabel-files.txt` from the pre-merge commit (your version).
4. Commits the merge.

Result: you get the latest RustDesk changes, but logo, icons, `Cargo.toml` metadata, and any other whitelabel paths stay as MultiDesk.

**Sync from a different upstream branch:**

```bash
./scripts/sync_upstream.sh main
```

## Manual sync (if you prefer or if the script fails)

```bash
git fetch upstream
git merge upstream/master --no-commit --no-ff
# Restore our whitelabel files (replace COMMIT with your branch’s pre-merge commit)
git checkout COMMIT -- $(grep -v '^#' scripts/whitelabel-files.txt | grep -v '^$' | tr '\n' ' ')
git add -A && git commit -m "Merge upstream/master (whitelabel preserved)"
```

## Merge conflicts

If `git merge` reports conflicts:

1. Resolve conflicts as usual (e.g. in your editor).
2. `git add` the resolved files.
3. Restore whitelabel files from the commit you had *before* the merge:
   ```bash
   git checkout PRE_MERGE_COMMIT -- $(grep -v '^#' scripts/whitelabel-files.txt | grep -v '^$' | tr '\n' ' ')
   ```
4. `git add -A && git commit` to finish the merge.

## What’s in the whitelabel list

- **Cargo.toml** – product name, copyright, Windows metadata.
- **res/icon.png**, **res/mac-icon.png**, **res/icon.ico**, **res/tray-icon.ico**, **flutter/windows/runner/resources/app_icon.ico** – app and tray icons.
- **flutter/assets/logo.png**, **flutter/assets/icon.png** – in-app logo and icon.
- **scripts/update_icons_from_png.py** – icon build script (e.g. 128px size).

To keep more customizations (e.g. About dialog, app name in code), add the relevant paths to `scripts/whitelabel-files.txt`. See `WHITELABEL_OPTIONS.md` for what’s customizable.

## After syncing

1. Build and test: `cargo build --release` and/or Flutter build.
2. If upstream changed dependencies or build steps, follow any new instructions in RustDesk’s README or docs.
3. Push your branch when ready: `git push origin master` (or your branch name).
