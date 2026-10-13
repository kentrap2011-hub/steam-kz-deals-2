#!/usr/bin/env python3
"""Regression for the SVG-only gamepad-icon transition (no binary PNG claim)."""

import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

WEB = Path(__file__).resolve().parents[1] / "web"
VERSION = "gamepad-svg-v1"
EMBEDDED_WEBP_SHA256 = "1df89d8e1c8f20d87c69e3863b2d66b67f76e6101d49ca5d8fe3b1aef66f3d98"
SVG = "{http://www.w3.org/2000/svg}"


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            self.links.append(dict(attrs))


def read_svg(filename):
    root = ET.parse(WEB / filename).getroot()
    assert root.tag == SVG + "svg"
    assert root.attrib.get("viewBox") == "0 0 512 512"
    assert "script" not in (WEB / filename).read_text(encoding="utf-8").lower()
    images = list(root.iter(SVG + "image"))
    assert len(images) == 1, f"{filename}: image count"
    image = images[0]
    assert image.attrib.get("width") == "512" and image.attrib.get("height") == "512"
    source = image.attrib["href"]
    assert source.startswith("data:image/webp;base64,")
    payload = base64.b64decode(source.split(",", 1)[1], validate=True)
    assert len(payload) == 9008 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
    assert hashlib.sha256(payload).hexdigest() == EMBEDDED_WEBP_SHA256
    assert not any(x.attrib.get("href", "").startswith(("http:", "https:")) for x in root.iter())
    return root, payload


def run():
    normal, normal_bytes = read_svg("icon.svg")
    maskable, mask_bytes = read_svg("icon-maskable.svg")
    assert normal_bytes == mask_bytes, "Maskable must retain the approved picture"
    assert len(list(normal.iter(SVG + "rect"))) == 0
    rects = list(maskable.iter(SVG + "rect"))
    assert len(rects) == 1 and rects[0].attrib == {
        "width": "512", "height": "512", "fill": "#000105"
    }
    groups = list(maskable.iter(SVG + "g"))
    assert len(groups) == 1
    assert groups[0].attrib.get("transform") == "translate(71.68 71.68) scale(.72)"
    # Maskable safe-zone diameter is 80% of canvas. The important controller/
    # percent ink of the supplied artwork (within ~[65,445] × [100,405]) is
    # centered and scales into a radius < 205 px, not clipped by the mask.
    for x, y in ((65,100),(445,100),(65,405),(445,405)):
        transformed_x = 71.68 + .72*x
        transformed_y = 71.68 + .72*y
        assert ((transformed_x-256)**2 + (transformed_y-256)**2)**.5 < 204.8

    manifest = json.loads((WEB / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["start_url"] == manifest["scope"] == "./"
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == manifest["background_color"] == "#0e1117"
    assert len(manifest["icons"]) == 2
    for icon, expected_name, expected_purpose in zip(
        manifest["icons"], ("icon.svg", "icon-maskable.svg"), ("any", "maskable")
    ):
        assert icon["type"] == "image/svg+xml" and icon["sizes"] == "any"
        assert icon["purpose"] == expected_purpose
        assert icon["src"] == f"{expected_name}?v={VERSION}"
        assert (WEB / urlsplit(icon["src"]).path).is_file()

    for filename in ("index.html", "tasks.html"):
        page = PageLinks()
        page.feed((WEB / filename).read_text(encoding="utf-8"))
        favicons = [x for x in page.links if "icon" in (x.get("rel") or "").split()]
        assert len(favicons) == 1
        assert favicons[0]["href"] == f"icon.svg?v={VERSION}"
        assert favicons[0]["type"] == "image/svg+xml"
        assert (WEB / urlsplit(favicons[0]["href"]).path).is_file()
        manifests = [x for x in page.links if "manifest" in (x.get("rel") or "").split()]
        assert len(manifests) == 1
        assert manifests[0]["href"] == f"manifest.webmanifest?v={VERSION}"
        assert (WEB / urlsplit(manifests[0]["href"]).path).is_file()
        assert not any("apple-touch-icon" in (x.get("rel") or "") for x in page.links), (
            "Do not claim Apple PNG support before uploading a real PNG"
        )
    print("PASS: approved embedded artwork, maskable safe zone, SVG MIME/path/version,")
    print("      manifest PWA launch properties and both HTML entry points")


if __name__ == "__main__":
    run()
