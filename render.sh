#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUTPUT=${1:-"$ROOT/entry.png"}
# Chromium is blocked by the sandbox socket policy.
# Render the exact inline SVG through librsvg/Cairo; check extents with Pillow.
python3 "$ROOT/fit.py" "$OUTPUT"
