#!/bin/sh
set -eu

CHROME=/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUTPUT=${1:-/output/entry.png}
CAPTURE=$ROOT/full.png
mkdir -p "$(dirname -- "$OUTPUT")"

if [ -x "$CHROME" ] && "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --screenshot="$CAPTURE" --window-size=1024,1200 "file://$ROOT/news.html" 2>/dev/null; then
  python3 "$ROOT/fit.py" "$CAPTURE" "$OUTPUT"
else
  python3 "$ROOT/fit.py" "$OUTPUT"
fi
