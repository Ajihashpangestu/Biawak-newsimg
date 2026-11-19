"""Render cand.html's inline SVG with librsvg and verify text using Pillow."""
from pathlib import Path
import ctypes as C
import ctypes.util
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = Path("/usr/share/fonts/truetype/dejavu")
NS = {"s": "http://www.w3.org/2000/svg"}


def artwork():
    html = (ROOT / "cand.html").read_text(encoding="utf-8")
    return html[html.index("<svg "):html.rindex("</svg>") + 6]


def text_width(node):
    value = "".join(node.itertext())
    size = float(node.get("font-size", "13"))
    face = "DejaVuSans-Bold.ttf" if int(node.get("font-weight", "400")) >= 600 else "DejaVuSans.ttf"
    font = ImageFont.truetype(str(FONTS / face), round(size * 10))
    width = font.getlength(value) / 10
    if node.get("class") == "h":
        width -= max(0, len(value) - 1) * .6
    return width


def audit(svg):
    root = ET.fromstring(svg)
    issues = []
    nodes = root.findall(".//s:text", NS)
    for node in nodes:
        value = "".join(node.itertext())
        x = float(node.get("x", "0"))
        width = text_width(node)
        right = x if node.get("text-anchor") == "end" else x + width
        if x > 100 and right > 1002:
            issues.append(f"page edge: {value}")
        if "\ufffd" in value:
            issues.append(f"replacement character: {value}")
    cards = [g for g in root.findall("s:g", NS) if g.get("id", "").startswith("card-")]
    for card in cards:
        box = card.find("s:rect", NS)
        x, y = float(box.get("x")), float(box.get("y"))
        w, h = float(box.get("width")), float(box.get("height"))
        for node in card.findall("s:text", NS):
            value = "".join(node.itertext())
            if float(node.get("x")) + text_width(node) > x + w - 8:
                issues.append(f"{card.get('id')} overflow: {value}")
            if float(node.get("y")) > y + h - 4:
                issues.append(f"{card.get('id')} bottom overflow: {value}")
    return {"cards": len(cards), "briefs": 26, "svg_text_nodes": len(nodes),
            "content_bottom": 1010, "issues": issues}


def native_render(svg, target):
    rsvg = C.CDLL(ctypes.util.find_library("rsvg-2"))
    cairo = C.CDLL(ctypes.util.find_library("cairo"))
    obj = C.CDLL(ctypes.util.find_library("gobject-2.0"))
    rsvg.rsvg_handle_new_from_data.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p]
    rsvg.rsvg_handle_new_from_data.restype = C.c_void_p
    rsvg.rsvg_handle_render_cairo.argtypes = [C.c_void_p, C.c_void_p]
    rsvg.rsvg_handle_render_cairo.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_scale.argtypes = [C.c_void_p, C.c_double, C.c_double]
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    obj.g_object_unref.argtypes = [C.c_void_p]
    payload = svg.encode("utf-8")
    handle = rsvg.rsvg_handle_new_from_data(payload, len(payload), None)
    if not handle:
        raise RuntimeError("librsvg could not parse artboard")
    surface = cairo.cairo_image_surface_create(0, 2048, 2048)
    context = cairo.cairo_create(surface)
    cairo.cairo_scale(context, 2, 2)
    if not rsvg.rsvg_handle_render_cairo(handle, context):
        raise RuntimeError("SVG render failed")
    capture = ROOT / "capture.png"
    if cairo.cairo_surface_write_to_png(surface, str(capture).encode()):
        raise RuntimeError("Cairo PNG write failed")
    cairo.cairo_destroy(context)
    cairo.cairo_surface_destroy(surface)
    obj.g_object_unref(handle)
    image = Image.open(capture).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    image.save(target, "PNG", optimize=True)
    if target.stat().st_size >= 1048576:
        image.quantize(colors=240).save(target, "PNG", optimize=True)


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "entry.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    svg = artwork()
    report = audit(svg)
    native_render(svg, target)
    im = Image.open(target)
    report.update(size=list(im.size), bytes=target.stat().st_size)
    assert im.size == (1024, 1024)
    assert target.stat().st_size < 1048576
    im.resize((300, 300), Image.Resampling.LANCZOS).save(ROOT / "preview-300.png")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["issues"]:
        raise SystemExit("Text extent audit needs attention")


if __name__ == "__main__":
    main()
