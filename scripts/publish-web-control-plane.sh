#!/usr/bin/env bash
# Publish the full single-file web control plane to GitHub (requires: gh auth login).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="${1:-$ROOT/web/server-os.html}"
test -f "$FILE" || { echo "missing $FILE"; exit 1; }
SIZE=$(wc -c < "$FILE")
echo "Publishing $FILE ($SIZE bytes) -> web/server-os.html"
CONTENT_B64=$(base64 -w0 < "$FILE" 2>/dev/null || base64 < "$FILE" | tr -d '\n')
SHA=$(gh api repos/ANAMIZED/server-os/contents/web/server-os.html --jq .sha 2>/dev/null || true)
ARGS=(--method PUT repos/ANAMIZED/server-os/contents/web/server-os.html
  -f message="feat: full web control plane v1.0-web (${SIZE} bytes)"
  -f content="$CONTENT_B64"
  -f branch=main)
if [[ -n "${SHA:-}" ]]; then ARGS+=(-f sha="$SHA"); fi
gh api "${ARGS[@]}"
echo "Done."
echo "Open: https://github.com/ANAMIZED/server-os/blob/main/web/server-os.html"
echo "Or:   python -m http.server 8088 --directory web"
