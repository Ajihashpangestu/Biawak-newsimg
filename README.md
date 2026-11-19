[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

# World news — Wednesday 18 November 2026

A one-image world news front page with a date-first giant title and a **THE DAY IN NUMBERS** band containing 8 sourced stats. It features 13 illustrated cards, 30 numbered briefs (14–43), a world map with numbered pins, and story locators.

The **DATE CHECK** footer lists stories excluded because they were first reported on 17 November: the Prague train crash and AP's Peltola race call.

Everything is rendered from `cand.html` via headless Chromium. Run `bash render.sh` to regenerate `entry.png`. The renderer captures a 1024×1300 viewport, crops content against the background with a small margin, and resizes with LANCZOS to exactly 1024×1024.

`fit.py` accepts an optional output path (default `entry.png`) and prints dimensions and byte size as JSON. `main.ts` is a Node 22 TypeScript entrypoint that reads `entry.png` in the repository root and prints its byte size and SHA-256 hash as JSON.
