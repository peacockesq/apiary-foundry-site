#!/usr/bin/env python3
"""Apply the approved Apiary Foundry brand shell to every static route.

This migration is intentionally narrow: it normalizes shared assets, theme metadata,
cache-busting, navigation branding, and the footer shell without changing page copy.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260801-kit-v3"
LEAD_ASSET_VERSION = "20260801-kit-v2"
SKIP_PARTS = {".git", "node_modules", "playwright-report", "test-results"}

NAV_BRAND = (
    '<a class="brand" href="/" aria-label="Apiary Foundry home">'
    '<img class="brand-logo" src="/assets/brand/logos/logo-horizontal-light.svg" '
    'width="196" height="52" alt="Apiary Foundry" />'
    '</a>'
)

FOOTER_START = (
    '<footer class="site-footer"><div class="container footer-inner">'
    '<a class="footer-brand" href="/" aria-label="Apiary Foundry home">'
    '<img src="/assets/brand/logos/logo-horizontal-dark.svg" width="220" height="59" '
    'alt="Apiary Foundry" /></a><div class="footer-meta">'
)
FOOTER_END = '</div></div></footer>'


def site_html_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def update_html(path: Path) -> bool:
    original = path.read_text()
    text = original
    text = re.sub(
        r'/assets/site\.css\?v=[^"\']+',
        f'/assets/site.css?v={ASSET_VERSION}',
        text,
    )
    text = re.sub(
        r'/assets/apiary-lead-capture\.js\?v=[^"\']+',
        f'/assets/apiary-lead-capture.js?v={LEAD_ASSET_VERSION}',
        text,
    )
    text = re.sub(
        r'<meta name="theme-color" content="#[0-9A-Fa-f]{6}"\s*/>',
        '<meta name="theme-color" content="#0F0F10" />',
        text,
    )
    text = re.sub(
        r'<a class="brand" href="/" aria-label="Apiary Foundry home">.*?</a>(?=<button class="hamburger")',
        NAV_BRAND,
        text,
        flags=re.DOTALL,
    )
    if 'class="site-footer"' not in text:
        text = re.sub(
            r'<footer class="container">(.*?)</footer>',
            lambda match: FOOTER_START + match.group(1) + FOOTER_END,
            text,
            flags=re.DOTALL,
        )
    text = text.replace(
        'alt="Apiary Foundry" loading="lazy" /></a><div class="footer-meta">',
        'alt="Apiary Foundry" /></a><div class="footer-meta">',
    )
    if text == original:
        return False
    path.write_text(text)
    return True


def update_generator() -> bool:
    path = ROOT / "scripts" / "build_content_site.py"
    original = path.read_text()
    text = re.sub(r"ASSET_VERSION = '[^']+'", f"ASSET_VERSION = '{ASSET_VERSION}'", original)
    text = re.sub(
        r'/assets/apiary-lead-capture\.js\?v=[^"\']+',
        f'/assets/apiary-lead-capture.js?v={LEAD_ASSET_VERSION}',
        text,
    )
    text = re.sub(
        r'<a class="brand" href="/" aria-label="Apiary Foundry home">.*?</a>(?=<button class="hamburger")',
        NAV_BRAND,
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        '  <footer class="container"><span>&copy; 2026 Apiary Foundry.</span><span><a href="/privacy-policy/">Privacy Policy</a> · <a href="/terms-of-service/">Terms of Service</a></span></footer>',
        '  ' + FOOTER_START + '<span>&copy; 2026 Apiary Foundry.</span><span><a href="/privacy-policy/">Privacy Policy</a> · <a href="/terms-of-service/">Terms of Service</a></span>' + FOOTER_END,
    )
    text = text.replace('<meta name="theme-color" content="#171512" />', '<meta name="theme-color" content="#0F0F10" />')
    text = text.replace(
        'alt="Apiary Foundry" loading="lazy" /></a><div class="footer-meta">',
        'alt="Apiary Foundry" /></a><div class="footer-meta">',
    )
    if text == original:
        return False
    path.write_text(text)
    return True


def main() -> None:
    changed = [path for path in site_html_files() if update_html(path)]
    generator_changed = update_generator()
    print(f"Updated {len(changed)} HTML routes; generator_changed={generator_changed}")


if __name__ == "__main__":
    main()
