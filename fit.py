#!/usr/bin/env python3
"""Render cand.html and fit its content to a square PNG."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
BACKGROUND = (247, 245, 239)
CROP_TOLERANCE = 8
CROP_MARGIN = 8

def main():
    output = (Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'entry.png').resolve()
    subprocess.run([
        '/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome',
        '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
        '--screenshot=full.png', '--window-size=1024,1300',
        (ROOT / 'cand.html').as_uri(),
    ], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with Image.open(ROOT / 'full.png') as source:
        image = source.convert('RGB')
    difference = ImageChops.difference(image, Image.new('RGB', image.size, BACKGROUND))
    red, green, blue = difference.split()
    mask = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = mask.point(lambda value: 255 if value > CROP_TOLERANCE else 0)
    bounds = mask.getbbox()
    if bounds:
        left, top, right, bottom = bounds
        image = image.crop((max(0, left - CROP_MARGIN), max(0, top - CROP_MARGIN),
                            min(image.width, right + CROP_MARGIN),
                            min(image.height, bottom + CROP_MARGIN)))
    image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
    image.save(output, format='PNG')
    print(json.dumps({'output': str(output), 'size': list(image.size),
                      'bytes': output.stat().st_size}))

if __name__ == '__main__':
    main()
