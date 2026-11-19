# 18 November 2026 — a day in the world

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![Rank](https://make.fun/badge/news-image-20261118/Ajihashpangestu/Biawak-newsimg/rank.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![Reward](https://make.fun/badge/news-image-20261118/Ajihashpangestu/Biawak-newsimg/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A new card atlas: giant date masthead, 13 illustrated cards, 26 numbered briefs (14–39), Natural Earth locator map, and date-check footer. Some briefs extend the context of cards; this does not claim 39 distinct stories.

## Build

Run `sh render.sh` for local `entry.png`. Run `node main.ts` on Node with native TypeScript support to render and copy it to `/output/entry.png`. Output: exactly 1024 × 1024, under 1,048,576 bytes.

`cand.html` contains the complete inline SVG artboard, including the supplied `world.svg` paths. Illustrations are hand-drawn vectors. No external images, other entries or AI bitmap assets are used.

The renderer reads the exact SVG from the HTML and uses system librsvg/Cairo, followed by Pillow antialiasing, size verification and text-extent checks. Chromium cannot launch under the sandbox's socket policy. Binary auxiliary images: `capture.png` (supersampled) and `preview-300.png` (thumbnail).

## Editorial scope

News copy follows the user-supplied reporting notes for Wednesday 18 November 2026. Searches produced no usable independently verifiable results in this environment. Malformed IPO and oil prices are omitted rather than guessed. Thursday events are explicitly scheduled. Military claims retain attribution. AFCON matchday four is excluded per the requested date-check footer; the FIFA election brief supplies sport.

Date-check exclusions reproduce the supplied editorial instructions; they have not been independently established here. Their inclusion is an editorial filter, not an assertion that every excluded report was accurate.

## Review

Two self-review rounds completed: the first identified crowded headings and illustration collisions; these were corrected by shortening headlines and reserving the top corner for compact icons. The second reviewed the corrected full-size image and 300px thumbnail. Pillow reports zero text-extent issues. Dense supporting briefs require full-resolution viewing; the date and main headlines have priority at 300px.

Final verification: 13 cards, 26 briefs, content ends at y=1010, PNG 1024 × 1024 and 699,233 bytes. PNG integrity verified. All six source/documentation files were written through apply_patch. The supplied world.svg was not changed.

The local entry.png was rendered successfully. The main.ts copy step was executed but /output is mounted read-only (EROFS), so /output/entry.png could not be created in this environment. The copy step remains implemented for execution in a writable output environment.

## License

Original layout and illustrations: MIT, see LICENSE. Supplied Natural Earth outline retained as provided. News facts attributed in the image where supplied.
