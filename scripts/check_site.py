#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re, sys

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text()
css = (root / "assets" / "site.css").read_text()

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
required = ["Apiary Foundry", "Growth systems for companies that are done guessing", "Growth Strategy Hive", "Acquisition Swarm", "Measurement & Compliance Swarm"]
for text in required:
    if text not in html: errors.append(f"missing required text: {text}")
for href in p.links:
    if href.startswith("#") and href[1:] not in p.ids:
        errors.append(f"broken anchor: {href}")
for asset in re.findall(r'href="(/assets/[^"]+)"', html):
    if not (root / asset.lstrip('/')).exists(): errors.append(f"missing asset: {asset}")
if "INTERNAL MOCKUP" in html or "PUBLIC CLAIMS NEED APPROVAL" in html:
    errors.append("internal mockup language leaked")
if len(css) < 5000: errors.append("css unexpectedly small")
if errors:
    print("FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print("OK: site checks passed")
