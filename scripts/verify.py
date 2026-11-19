"""Check the news atlas in cand.html. Text metrics require Pillow and DejaVu Sans."""

import json
import re
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree as ET


SVG = "{http://www.w3.org/2000/svg}"
TEXT = SVG + "text"
SOURCE_TAG = re.compile(r"\([^()]*\bNov[^()]*\)\Z")
STAT_VALUE = re.compile(r"[$€£]?\d[\d,.]*(?:-\d+)?(?:%|[A-Za-z]+(?: [A-Za-z]+)?)?")
METRIC_SCALE = 32


def content(node):
    return " ".join("".join(node.itertext()).split())


def check_cards(svg, issues):
    groups = [
        group for group in svg.iter(SVG + "g")
        if re.fullmatch(r"card-\d+", group.get("id", ""))
    ]
    count = 0
    for group in groups:
        labels = group.findall(TEXT)
        # Each card starts with a numbered topic label followed by its headline.
        if (len(labels) >= 2 and re.match(r"\d+ / ", content(labels[0]))
                and content(labels[1])):
            count += 1
        else:
            issues.append(f"{group.get('id')} has no title")
    if count != 13:
        issues.append(f"Expected 13 card titles, found {count}")
    return count


def check_briefs(svg, issues):
    labels = svg.findall(TEXT)
    start = next((i for i, node in enumerate(labels)
                  if content(node).startswith("ALSO ON ")), None)
    end = next((i for i, node in enumerate(labels)
                if content(node).startswith("WORLD / STORY LOCATORS")), None)
    if start is None or end is None or end <= start:
        issues.append("Could not locate the ALSO list")
        return 0

    rows = labels[start + 1:end]
    if rows and re.match(r"\d+-\d+ / ", content(rows[0])):
        rows = rows[1:]
    numbers = []
    for i in range(0, len(rows), 2):
        number = content(rows[i])
        numbers.append(int(number) if re.fullmatch(r"[0-9]+", number) else number)
        if i + 1 == len(rows) or rows[i].get("y") != rows[i + 1].get("y"):
            issues.append(f"Brief {number!r} has no matching text on its row")
        elif not SOURCE_TAG.search(content(rows[i + 1])):
            issues.append(f"Brief {number!r} is missing a final source tag containing Nov")
    if numbers != list(range(14, 44)):
        issues.append(f"Expected consecutive brief numbers 14–43, found {numbers}")
    return len(numbers)


def check_band(svg, issues):
    band = svg.find(f".//{SVG}g[@id='stat-band']")
    count = 0 if band is None else sum(
        bool(STAT_VALUE.fullmatch(content(node))) for node in band.iter(TEXT)
    )
    if count != 8:
        issues.append(f"Expected 8 stat numbers, found {count}")
    return count


@lru_cache(maxsize=None)
def font_for(size, bold):
    from PIL import ImageFont

    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(name, round(size * METRIC_SCALE))


def check_bounds(svg, issues):
    for node in svg.iter(TEXT):
        label = content(node)
        size = float(node.get("font-size", "16"))
        if size <= 9 or not label:
            continue
        x, y = float(node.get("x", "0")), float(node.get("y", "0"))
        font = font_for(size, int(node.get("font-weight", "400")) >= 600)
        spacing = float(node.get("letter-spacing", "-.6" if "h" in
                                 node.get("class", "").split() else "0"))
        gaps = spacing * (len(label) - 1)
        advance = font.getlength(label) / METRIC_SCALE + gaps
        anchor = node.get("text-anchor", "start")
        origin = x - advance * {"start": 0, "middle": 0.5, "end": 1}[anchor]
        left, top, right, bottom = (
            value / METRIC_SCALE for value in font.getbbox(label, anchor="ls")
        )
        right += origin + gaps
        left += origin
        top += y
        bottom += y
        if not (x >= 24 and left >= 24 and right <= 1000 and 20 <= top <= bottom <= 1010):
            issues.append(
                f"Text {label!r} is out of bounds "
                f"(x={x:g}, left={left:.2f}, right={right:.2f}, "
                f"top={top:.2f}, bottom={bottom:.2f})"
            )


def main():
    report = {"cards": 0, "briefs": 0, "band_stats": 0, "issues": []}
    issues = report["issues"]
    try:
        html = (Path(__file__).resolve().parents[1] / "cand.html").read_text(encoding="utf-8")
        start = html.index("<svg")
        end = html.rindex("</svg>") + len("</svg>")
        svg = ET.fromstring(html[start:end])
        report["cards"] = check_cards(svg, issues)
        report["briefs"] = check_briefs(svg, issues)
        report["band_stats"] = check_band(svg, issues)
        check_bounds(svg, issues)
    except (ET.ParseError, ImportError, KeyError, OSError, ValueError) as error:
        issues.append(f"Could not complete verification: {error}")
    print(json.dumps(report, ensure_ascii=False))
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
