"""Offline renderer for news.html; HTML is the only editorial source."""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image, ImageDraw, ImageFont
import re

ROOT = Path(__file__).resolve().parent
BG, INK, MUTED, ACCENT, RULE = "#f7f4eb", "#171c21", "#465159", "#a52d22", "#d4d2c8"
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bands, self.land, self.circles, self.labels = [], [], [], []
        self.matrix = ()
        self.leaders = []
        self.current = None
        self.capture = None
        self.parts = []
        self.lead = {}
        self.in_lead = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.in_lead = a.get("class") == "lead"
            if "band" in a.get("class", "").split():
                self.current = {"title": "", "stories": [], "dense": "dense" in a.get("class", "")}
                self.bands.append(self.current)
        if tag == "article":
            self.current["stories"].append({})
        if tag in ("h1", "h2", "h3", "p", "text") or (tag == "div" and a.get("class") in ("brand", "date", "kicker")):
            self.capture = (tag, a)
            self.parts = []
        if tag == "g" and a.get("class") == "land":
            self.matrix = tuple(map(float, a["transform"].removeprefix("matrix(").removesuffix(")").split()))
        if tag == "path":
            paths = [[tuple(map(float, pair.split(","))) for pair in subpath.split()]
                     for subpath in re.findall(r"M\s+([^MZ]+)", a["d"])]
            if a.get("class") == "leaders":
                self.leaders.extend(paths)
            else:
                self.land.extend(paths)
        if tag == "circle":
            self.circles.append(a)
    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if self.capture and tag == self.capture[0]:
            kind, a = self.capture
            value = "".join(self.parts)
            if kind == "text":
                self.labels.append((float(a["x"]), float(a["y"]), value))
            elif kind == "h2":
                self.current["title"] = value
            elif kind == "h3" or (kind == "p" and not self.in_lead):
                self.current["stories"][-1]["headline" if kind == "h3" else "fact"] = value
            else:
                self.lead[a.get("class", kind)] = value
            self.capture = None
        if tag == "section":
            self.in_lead = False

page = Page()
page.feed((ROOT / "news.html").read_text())
img = Image.new("RGB", (1024, 1024), BG)
d = ImageDraw.Draw(img)
fonts = Path("/usr/share/fonts/truetype/dejavu")
def font(size, face="sans"):
    name = {"sans": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf", "serif": "DejaVuSerif-Bold.ttf"}[face]
    return ImageFont.truetype(str(fonts / name), size)
def text(x, y, value, size, face="sans", color=INK):
    d.text((x, y), value, font=font(size, face), fill=color, anchor="lt")
def center(y, value, size, face="bold", color=INK):
    w = d.textlength(value, font=font(size, face))
    text((1024-w)/2, y, value, size, face, color)
def wrap(value, width, size, face="sans"):
    lines, line = [], ""
    for word in value.split():
        trial = (line + " " + word).strip()
        if line and d.textlength(trial, font=font(size, face)) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines
def paragraph(x, y, value, width, size, step, face="sans", color=INK):
    for line in wrap(value, width, size, face):
        text(x, y, line, size, face, color)
        y += step
    return y
def rule(y, x=26, width=972, weight=1):
    d.rectangle((x, y, x+width, y+weight-1), fill=INK if weight > 1 else RULE)

rule(16, weight=6)
center(24, page.lead["brand"], 60, "serif")
center(83, page.lead["date"], 17)
rule(103, weight=3)
text(26, 113, page.lead["kicker"], 15, "bold", ACCENT)
text(26, 132, page.lead["h1"], 44, "serif")
paragraph(26, 177, page.lead["p"], 972, 17, 20)
rule(217, weight=2)

# Project the same longitude/latitude paths and annotations as the inline SVG.
ox, oy = 26, 226
a, b, c, e, tx, ty = page.matrix
for points in page.land:
    d.polygon([(ox + a*x + c*y + tx, oy + b*x + e*y + ty) for x, y in points],
              fill="#d5d4c8", outline=BG)
for points in page.leaders:
    d.line([(ox+x, oy+y) for x, y in points], fill=ACCENT)
for marker in page.circles:
    x, y, r = map(float, (marker["cx"], marker["cy"], marker["r"]))
    d.ellipse((ox+x-r, oy+y-r, ox+x+r, oy+y+r), fill=ACCENT, outline=BG)
for x, y, value in page.labels:
    d.text((ox+x, oy+y), value, font=font(14, "bold"), fill=ACCENT, anchor="ls", stroke_width=1, stroke_fill=BG)
rule(350)

# Panels use typography and spacing appropriate to their story counts.
bounds = []
for i, band in enumerate(page.bands):
    x = 26 + (i % 3) * 330
    y = 358 if i < 3 else 645
    width, bottom = 312, 634 if i < 3 else 978
    rule(y, x, width, 4)
    text(x, y+9, band["title"], 25, "bold", ACCENT)
    cy = y + 39
    headline_step, fact_step, pad = (19, 16, 0) if band["dense"] else (21, 17, 3)
    for story in band["stories"]:
        d.line((x, cy, x+width-1, cy), fill=RULE)
        cy = paragraph(x, cy+pad+1, story["headline"], width, 19, headline_step, "serif")
        cy = paragraph(x, cy, story["fact"], width, 15, fact_step, "sans", MUTED)+pad+int(not pad)
    bounds.append({"band": band["title"], "bottom": cy, "limit": bottom})
rule(985, weight=3)
text(26, 994, "18 NOVEMBER 2026 · WORLD EDITION", 12, "bold")
edition = "31 STORIES · SIX NEWS BANDS"
text(998-d.textlength(edition, font=font(12, "bold")), 994, edition, 12, "bold")
assert all(b["bottom"] <= b["limit"] for b in bounds), bounds
assert len(page.bands) == 6
assert sum(len(b["stories"]) for b in page.bands) == 30
for band in page.bands:
    for story in band["stories"]:
        assert 2 <= len(story["headline"].split()) <= 5, story
img.save(ROOT / "entry.png", optimize=True)
print({"story_count": 31, "bounds": bounds})
