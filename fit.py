"""Fit a browser capture, or render the HTML's news content with Pillow."""

from html.parser import HTMLParser
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SIDE = 1024
PAPER = "#f7f4eb"
INK = "#171c21"
MUTED = "#465159"
RULE = "#d4d2c8"
RED = "#a52d22"
FONT_ROOT = Path("/usr/share/fonts/truetype/dejavu")


class Newspaper(HTMLParser):
    """Read headlines and facts from the page, keeping HTML as the copy source."""

    def __init__(self):
        super().__init__()
        self.sections = []
        self.lead = {}
        self.footer = []
        self.active_band = None
        self.active_story = None
        self.active_tag = None
        self.active_key = None
        self.buffer = []
        self.in_lead = False
        self.in_footer = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.in_lead = "lead" in attrs.get("class", "").split()
            if "band" in attrs.get("class", "").split():
                self.active_band = {
                    "title": "",
                    "stories": [],
                    "compact": "compact" in attrs.get("class", "").split(),
                }
                self.sections.append(self.active_band)
        elif tag == "article" and self.active_band:
            self.active_story = {}
            self.active_band["stories"].append(self.active_story)
        elif tag == "footer":
            self.in_footer = True
        elif tag in {"h1", "h2", "h3", "p"}:
            self.active_tag = tag
            self.active_key = tag
            self.buffer = []

    def handle_data(self, data):
        if self.active_tag:
            self.buffer.append(data)
        if self.in_footer and data.strip():
            self.footer.append(data.strip())

    def handle_endtag(self, tag):
        if self.active_tag == tag:
            value = " ".join("".join(self.buffer).split())
            if tag == "h1":
                self.lead[tag] = value
            elif self.in_lead and tag == "p":
                self.lead[tag] = value
            elif tag == "h2" and self.active_band:
                self.active_band["title"] = value
            elif tag == "h3" and self.active_story is not None:
                self.active_story["headline"] = value
            elif tag == "p" and self.active_story is not None:
                self.active_story["fact"] = value
            self.active_tag = self.active_key = None
            self.buffer = []
        elif tag == "article":
            self.active_story = None
        elif tag == "section":
            self.in_lead = False
            if self.active_band:
                self.active_band = None
        elif tag == "footer":
            self.in_footer = False


def font(size, face="sans"):
    names = {
        "sans": "DejaVuSans.ttf",
        "bold": "DejaVuSans-Bold.ttf",
        "serif": "DejaVuSerif-Bold.ttf",
    }
    return ImageFont.truetype(str(FONT_ROOT / names[face]), size)


def wrap(draw, value, width, selected_font):
    lines = []
    line = ""
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if line and draw.textlength(candidate, font=selected_font) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def draw_page(destination):
    parser = Newspaper()
    parser.feed((ROOT / "news.html").read_text(encoding="utf-8"))
    canvas = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((24, 12, 1000, 17), fill=INK)

    title_font = font(49, "serif")
    title = "THE WORLD"
    draw.text(((SIDE - draw.textlength(title, font=title_font)) / 2, 18), title,
              fill=INK, font=title_font)
    date_font = font(14, "bold")
    date = "WEDNESDAY NOVEMBER 18 2026"
    draw.text(((SIDE - draw.textlength(date, font=date_font)) / 2, 67), date,
              fill=INK, font=date_font)
    draw.rectangle((24, 91, 1000, 93), fill=INK)

    x, y = 26, 101
    draw.text((x, y), "THE LEAD / MIDDLE EAST", font=font(13, "bold"), fill=RED)
    y += 20
    draw.text((x, y), parser.lead["h1"], font=font(39, "serif"), fill=INK)
    y += 46
    lead_face = font(14)
    for line in wrap(draw, parser.lead["p"], 972, lead_face):
        draw.text((x, y), line, font=lead_face, fill=MUTED)
        y += 18
    draw.rectangle((24, 207, 1000, 209), fill=INK)

    # Use the same longitude / latitude projection as the locator strip.
    def project(longitude, latitude):
        return (512 + 2.48 * longitude, 264 - .58 * latitude)

    continents = [
        [(-168, 66), (-151, 71), (-135, 67), (-119, 68), (-104, 72), (-88, 65),
         (-78, 56), (-62, 50), (-71, 42), (-82, 26), (-96, 19), (-108, 23),
         (-119, 34), (-127, 47), (-140, 58), (-157, 57)],
        [(-80, 9), (-70, 12), (-61, 8), (-50, 2), (-37, -6), (-40, -17),
         (-49, -29), (-60, -40), (-68, -53), (-74, -43), (-71, -28),
         (-70, -17), (-80, -5)],
        [(-11, 36), (-7, 44), (2, 47), (8, 55), (19, 59), (28, 66),
         (42, 68), (55, 66), (70, 72), (86, 73), (102, 76), (119, 72),
         (137, 70), (157, 67), (174, 65), (164, 61), (153, 53), (144, 48),
         (135, 43), (128, 35), (122, 27), (112, 20), (105, 9), (94, 7),
         (84, 16), (76, 9), (70, 21), (59, 25), (48, 30), (39, 36),
         (28, 41), (18, 42), (10, 37), (2, 39)],
        [(-17, 15), (-13, 28), (-5, 35), (8, 37), (20, 33), (31, 31),
         (38, 20), (44, 11), (50, 3), (42, -8), (39, -16), (32, -28),
         (21, -35), (14, -27), (10, -15), (7, -5), (1, 5), (-10, 7)],
        [(113, -12), (122, -10), (133, -12), (145, -17), (153, -26),
         (149, -36), (140, -39), (129, -33), (117, -25)],
    ]
    for outline in continents:
        draw.polygon([project(lon, lat) for lon, lat in outline],
                     fill="#d5d4c8", outline=PAPER)
    draw.rectangle((24, 300, 1000, 301), fill=RULE)
    markers = [
        ("UKRAINE", project(31, 49), (606, 218), (602, 225)),
        ("GULF", project(52, 25), (650, 244), (646, 252)),
        ("SUDAN", project(30, 15), (610, 268), (605, 267)),
        ("CHINA", project(105, 35), (782, 237), (778, 246)),
        ("LATAM", project(-60, -10), (282, 277), (348, 281)),
        ("AFRICA", project(20, -2), (462, 283), (523, 284)),
    ]
    for label, (px, py), label_at, leader_to in markers:
        draw.line((px, py, *leader_to), fill=RED, width=1)
        draw.ellipse((px-4, py-4, px+4, py+4), fill=RED, outline=PAPER, width=1)
        draw.text(label_at, label, font=font(11, "bold"), fill=RED)
    draw.arc((119, 211, 908, 294), 190, 350, fill="#d5d4c8", width=2)

    panel_x = [26, 356, 686]
    panel_y = [313, 590]
    panel_w = 312
    for index, band in enumerate(parser.sections):
        x = panel_x[index % 3]
        y = panel_y[index // 3]
        draw.rectangle((x, y, x+panel_w, y+3), fill=INK)
        y += 8
        draw.text((x, y), band["title"], font=font(21, "bold"), fill=RED)
        y += 29
        dense = band["compact"] or len(band["stories"]) > 4
        headline_face = font(14 if dense else 15, "serif")
        fact_face = font(12)
        headline_step = 16 if dense else 17
        fact_step = 14 if dense else 15
        for story in band["stories"]:
            draw.line((x, y, x+panel_w-1, y), fill=RULE, width=1)
            y += 3
            for line in wrap(draw, story["headline"], panel_w, headline_face):
                draw.text((x, y), line, font=headline_face, fill=INK)
                y += headline_step
            for line in wrap(draw, story["fact"], panel_w, fact_face):
                draw.text((x, y), line, font=fact_face, fill=MUTED)
                y += fact_step
            y += 2

    draw.rectangle((24, 987, 1000, 990), fill=INK)
    footer = "18 NOVEMBER 2026 · WORLD EDITION | 31 STORIES · SIX NEWS BANDS"
    footer_face = font(11, "bold")
    footer_x = (SIDE - draw.textlength(footer, font=footer_face)) / 2
    draw.text((footer_x, 995), footer, font=footer_face, fill=INK)
    canvas.save(destination, format="PNG", optimize=True)


def fit_capture(source, destination):
    image = Image.open(source).convert("RGB")
    background = Image.new("RGB", image.size, (247, 244, 235))
    changed = ImageChops.difference(image, background).convert("L")
    visible = changed.point(lambda value: 255 if value > 8 else 0).getbbox()
    if visible is None:
        raise ValueError("No visible page content was found in the browser capture.")
    bottom = min(image.height, visible[3] + 6)
    fitted = image.crop((0, 0, image.width, bottom)).resize(
        (SIDE, SIDE), Image.Resampling.LANCZOS
    )
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    fitted.save(destination, format="PNG", optimize=True)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        draw_page(sys.argv[1])
    elif len(sys.argv) == 3:
        fit_capture(sys.argv[1], sys.argv[2])
    else:
        raise SystemExit("usage: fit.py output.png OR fit.py capture.png output.png")
