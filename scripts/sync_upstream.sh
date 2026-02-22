#!/usr/bin/env bash
# Sync MultiDesk with RustDesk upstream while keeping whitelabel files.
# Run from repo root. Usage: ./scripts/sync_upstream.sh [upstream_branch]
# Default upstream branch: master

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

UPSTREAM_BRANCH="${1:-master}"
WHITELABEL_LIST="$REPO_ROOT/scripts/whitelabel-files.txt"

# Ensure we're on a clean state (optional: uncomment to require clean tree)
# if ! git diff-index --quiet HEAD --; then
#   echo "Working tree has uncommitted changes. Commit or stash first."
#   exit 1
# fi

# Add upstream remote if not present
if ! git remote get-url upstream &>/dev/null; then
  echo "Adding remote 'upstream' -> https://github.com/rustdesk/rustdesk"
  git remote add upstream https://github.com/rustdesk/rustdesk
fi

echo "Fetching upstream..."
git fetch upstream

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BEFORE_MERGE="$(git rev-parse HEAD)"

echo "Merging upstream/$UPSTREAM_BRANCH into $CURRENT_BRANCH (keeping whitelabel files)..."
# Merge but don't commit so we can restore whitelabel files
if ! git merge "upstream/$UPSTREAM_BRANCH" --no-commit --no-ff; then
  echo "Merge had conflicts. Resolve them, then run:"
  echo "  git checkout $BEFORE_MERGE -- \$(grep -v '^#' $WHITELABEL_LIST | grep -v '^$' | tr '\\n' ' ')"
  echo "  git add -A && git commit -m 'Merge upstream/$UPSTREAM_BRANCH (whitelabel preserved)'"
  exit 1
fi

# Restore our version of whitelabel files (from before merge)
if [[ -f "$WHITELABEL_LIST" ]]; then
  paths=()
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line// /}"
    [[ -z "$line" ]] && continue
    if [[ -f "$REPO_ROOT/$line" ]] || git show "$BEFORE_MERGE:$line" &>/dev/null; then
      paths+=("$line")
    fi
  done < "$WHITELABEL_LIST"
  if [[ ${#paths[@]} -gt 0 ]]; then
    echo "Restoring whitelabel files from pre-merge commit..."
    git checkout "$BEFORE_MERGE" -- "${paths[@]}"
  fi
else
  echo "Warning: $WHITELABEL_LIST not found; no whitelabel paths restored."
fi

echo "Completing merge commit..."
git add -A
git commit -m "Merge upstream/$UPSTREAM_BRANCH into $CURRENT_BRANCH (whitelabel preserved)"

echo "Done. Review with: git log -1 --stat"
echo "If you added new branding files, add them to scripts/whitelabel-files.txt for next sync."
