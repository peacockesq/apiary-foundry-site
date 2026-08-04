#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
css = (root / "assets" / "site.css").read_text()
brand_tokens = (root / "assets" / "brand" / "tokens.css").read_text()

required_pages = {
    "": "The cure for random acts of marketing.",
    "about-willie-peacock/": "The operator who turned off the ads and nobody noticed.",
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
    "privacy-policy/": "Privacy Policy",
    "terms-of-service/": "Terms of Service",
    "blog/": "Operator notes on measurable growth.",
    "blog/deterministic-vs-agentic-marketing-systems/": "Deterministic vs. agentic marketing systems.",
    "trust/": "An attorney runs the system.",
    "proof/military-com/": "The ads were so bad that nobody noticed when they stopped.",
    "proof/upgradedpoints/": "43 consecutive profitable months.",
    "proof/spectraforce/": "Two weeks versus six months.",
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
        asset_path = asset.split("?", 1)[0]
        if not (root / asset_path.lstrip('/')).exists(): errors.append(f"missing asset: {asset}")

public_html = "\n".join(h for _, h in all_html)
for stale in [
    "5-Hive", "Hive5", "Hive Five", "INTERNAL MOCKUP", "PUBLIC CLAIMS NEED APPROVAL",
    "Suggested visual", "Design note", "Proof themes to use on this page", "Placeholder for future",
    "Working title", "Recommended case study categories", "Each AF case study should follow",
    "made Google reps speechless", "### Story", ">Story<", "System elements to highlight",
]:
    if stale in public_html:
        errors.append(f"stale/internal language leaked: {stale}")
if re.search(r"Five Hive(?!s)", public_html):
    errors.append("stale/internal language leaked: Five Hive")
if re.search(r"\b[Nn]ot [^.!?]{1,100}\bbut\b", public_html):
    errors.append("overused not-X-but-Y construction in public pages")
for required in ["operator-led growth system", "marketing and business process systems", "what gets measured gets funded", "Willie Peacock", "massive travel credit card affiliate"]:
    if required.lower() not in public_html.lower():
        errors.append(f"missing global phrase: {required}")
if len(css) < 10000:
    errors.append("css unexpectedly small")

for asset_name in [
    "assets/favicon.svg",
    "assets/apiary-lead-capture.js",
    "assets/brand/tokens.css",
    "assets/brand/logos/logo-horizontal-light.svg",
    "assets/brand/logos/logo-horizontal-dark.svg",
    "assets/brand/logos/mark-light.svg",
    "assets/brand/logos/mark-dark.svg",
    "assets/brand/patterns/honeycomb-corner.svg",
]:
    if not (root / asset_name).exists():
        errors.append(f"missing asset: {asset_name}")
if "/privacy-policy/" not in public_html or "/terms-of-service/" not in public_html:
    errors.append("missing legal footer/consent links")
if 'name="marketing_consent" type="checkbox" value="yes" required' not in public_html:
    errors.append("marketing consent checkbox is not explicitly required")
if "bookingUrlFor" not in (root / "assets" / "apiary-lead-capture.js").read_text():
    errors.append("lead capture script missing attribution-preserving booking URL helper")
if "@media(max-width:1080px){.nav-links{display:none}" in css:
    errors.append("mobile navigation is hidden without a replacement menu")
if "--af-amber-deep: #8C4F00" not in brand_tokens:
    errors.append("runtime brand tokens missing accessible deep amber")
for brand_system_required in [
    "@import url('/assets/brand/tokens.css?v=20260801-kit-v2')",
    "font-family: Oswald",
    "url('/assets/brand/patterns/honeycomb-corner.svg')",
    ".brand-logo",
    ".site-footer",
    "--amber-deep: var(--af-amber-deep)",
    "color: var(--amber-deep)",
    ".button:hover { background: var(--charcoal); color: var(--white); }",
    "border-radius: 2px",
    "prefers-reduced-motion: reduce",
    "transform: translateY(calc(-100% - 24px))",
]:
    if brand_system_required not in css:
        errors.append(f"missing approved brand-system rule: {brand_system_required}")
for mobile_required in [
    "Mobile density and readability pass",
    '.nav-links[aria-expanded="true"]',
    ".mobile-cta",
    ".lead-form input",
    ".newsletter-strip",
    ".hero-honeycomb { overflow: hidden; }",
    ".subpage:has(#diagnostic) .mobile-cta",
]:
    if mobile_required not in css:
        errors.append(f"missing responsive/mobile rule: {mobile_required}")
for rel_path, html in all_html:
    if 'class="brand-logo" src="/assets/brand/logos/logo-horizontal-light.svg"' not in html:
        errors.append(f"approved navigation lockup missing on /{rel_path.lstrip('/')}")
    if 'class="site-footer"' not in html or 'logo-horizontal-dark.svg' not in html:
        errors.append(f"approved dark footer lockup missing on /{rel_path.lstrip('/')}")
    if "/assets/site.css?v=20260801-kit-v2" not in html:
        errors.append(f"brand-system stylesheet version missing on /{rel_path.lstrip('/')}")
    if "/assets/apiary-lead-capture.js?v=20260801-kit-v2" not in html:
        errors.append(f"lead-capture asset version missing on /{rel_path.lstrip('/')}")
work_html = (root / "work-with-us" / "index.html").read_text()
if 'name="phone"' in work_html or 'name="company"' in work_html:
    errors.append("diagnostic form still asks for phone/company on the mobile-critical page")
if 'aria-label="Apiary engagement flow"' not in work_html:
    errors.append("work-with-us missing visual engagement flow break")
dockerfile = (root / "Dockerfile").read_text()
if "127.0.0.1:8080" not in dockerfile:
    errors.append("Docker healthcheck must use 127.0.0.1:8080")

required_docker_copy_paths = [
    "assets",
    "about-willie-peacock",
    "measurement-engine",
    "growth-os",
    "five-hives",
    "paid-media-acquisition",
    "seo-content-marketing",
    "conversion-rate-optimization",
    "lifecycle-crm",
    "marketing-measurement-attribution",
    "proof",
    "trust",
    "privacy-policy",
    "terms-of-service",
    "blog",
    "work-with-us",
]
for route in required_docker_copy_paths:
    expected = f"COPY {route} /usr/share/nginx/html/{route}"
    if expected not in dockerfile:
        errors.append(f"Dockerfile missing static route copy: {expected}")

if errors:
    print("FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print(f"OK: {len(required_pages)} pages passed content, route, copy, and asset checks")
