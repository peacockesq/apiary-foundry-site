#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
css = (root / "assets" / "site.css").read_text()

required_pages = {
    "": "The cure for random acts of marketing.",
    "about-willie-peacock/": "Human strategy. Machine-assisted execution. Operator accountability.",
    "measurement-engine/": "The infrastructure behind fundable marketing.",
    "growth-os/": "The operating system for measurable growth work.",
    "five-hives/": "Five hives. One accountable growth system.",
    "paid-media-acquisition/": "Paid media should behave like capital allocation.",
    "seo-content-marketing/": "Content should earn attention and survive scrutiny.",
    "conversion-rate-optimization/": "Expensive traffic deserves disciplined pages.",
    "lifecycle-crm/": "The money often gets made after the first conversion.",
    "marketing-measurement-attribution/": "The hive that decides what gets funded.",
    "proof/": "Proof beats theater.",
    "work-with-us/": "Bring order to the marketing system.",
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=set(); self.links=[]; self.alts=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if "id" in d: self.ids.add(d["id"])
        if tag == "a" and "href" in d: self.links.append(d["href"])
        if tag == "img": self.alts.append(d.get("alt"))

errors=[]
all_html=[]
for rel_path, required_text in required_pages.items():
    page = root / rel_path / "index.html" if rel_path else root / "index.html"
    if not page.exists():
        errors.append(f"missing page: /{rel_path}")
        continue
    html = page.read_text()
    all_html.append((rel_path or '/', html))
    if required_text not in html:
        errors.append(f"missing required content on /{rel_path}: {required_text}")
    parser = LinkParser(); parser.feed(html)
    for href in parser.links:
        if href.startswith("#") and href[1:] not in parser.ids:
            errors.append(f"broken anchor on /{rel_path}: {href}")
        if href.startswith("/") and not href.startswith("//") and not href.startswith("/assets"):
            target = href.split('#')[0].strip('/')
            if target and not (root / target / "index.html").exists():
                errors.append(f"broken internal link on /{rel_path}: {href}")
    for asset in re.findall(r'href="(/assets/[^"]+)"', html):
        if not (root / asset.lstrip('/')).exists(): errors.append(f"missing asset: {asset}")

public_html = "\n".join(h for _, h in all_html)
for stale in ["5-Hive", "Hive5", "Hive Five", "INTERNAL MOCKUP", "PUBLIC CLAIMS NEED APPROVAL", "Suggested visual", "Design note", "Proof themes to use on this page", "Placeholder for future"]:
    if stale in public_html:
        errors.append(f"stale/internal language leaked: {stale}")
if re.search(r"Five Hive(?!s)", public_html):
    errors.append("stale/internal language leaked: Five Hive")
if re.search(r"\b[Nn]ot [^.!?]{1,100}\bbut\b", public_html):
    errors.append("overused not-X-but-Y construction in public pages")
for required in ["operator-led growth system", "floods of busy work", "what gets measured gets funded", "Willie Peacock", "Upgraded Points"]:
    if required.lower() not in public_html.lower():
        errors.append(f"missing global phrase: {required}")
if len(css) < 10000:
    errors.append("css unexpectedly small")
if "127.0.0.1:8080" not in (root / "Dockerfile").read_text():
    errors.append("Docker healthcheck must use 127.0.0.1:8080")

if errors:
    print("FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print(f"OK: {len(required_pages)} pages passed content, route, copy, and asset checks")
