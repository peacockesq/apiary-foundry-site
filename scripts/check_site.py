#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re, sys

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text()
css = (root / "assets" / "site.css").read_text()

required_pages = {
    "growth-strategy/": "Growth Strategy Hive",
    "acquisition/": "Acquisition Swarm",
    "conversion/": "Conversion Swarm",
    "content-seo/": "Content & SEO Swarm",
    "lifecycle/": "Lifecycle Swarm",
    "measurement-compliance/": "Measurement & Compliance Swarm",
    "about/": "About Apiary Foundry",
    "case-studies/": "Case Studies",
    "work-with-us/": "Work With Apiary Foundry",
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=set(); self.links=[]; self.alts=[]; self.titles=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if "id" in d: self.ids.add(d["id"])
        if tag == "a" and "href" in d: self.links.append(d["href"])
        if tag == "img": self.alts.append(d.get("alt"))
        if tag == "title": self._in_title=True

p=LinkParser(); p.feed(html)
errors=[]
required = ["Apiary Foundry", "cure for random acts of marketing", "operator-led growth system", "Growth Strategy Hive", "Acquisition Swarm", "Measurement & Compliance Swarm"]
for text in required:
    if text not in html: errors.append(f"missing required text: {text}")
for href in p.links:
    if href.startswith("#") and href[1:] not in p.ids:
        errors.append(f"broken anchor: {href}")
for asset in re.findall(r'href="(/assets/[^"]+)"', html):
    if not (root / asset.lstrip('/')).exists(): errors.append(f"missing asset: {asset}")
for rel_path, title in required_pages.items():
    page = root / rel_path / "index.html"
    if not page.exists():
        errors.append(f"missing page: {rel_path}")
        continue
    page_html = page.read_text()
    if title not in page_html:
        errors.append(f"missing title on {rel_path}: {title}")
    if "Five Hive" in page_html or "5-Hive" in page_html or "Hive5" in page_html:
        errors.append(f"stale hive naming leaked in {rel_path}")
    if re.search(r"\b[Nn]ot [^.!?]{1,80}\bbut\b", page_html):
        errors.append(f"overused not-X-but-Y construction in {rel_path}")
if "INTERNAL MOCKUP" in html or "PUBLIC CLAIMS NEED APPROVAL" in html:
    errors.append("internal mockup language leaked")
if re.search(r"\b[Nn]ot [^.!?]{1,80}\bbut\b", html):
    errors.append("overused not-X-but-Y construction on home page")
if len(css) < 5000: errors.append("css unexpectedly small")
if errors:
    print("FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print("OK: site checks passed")
