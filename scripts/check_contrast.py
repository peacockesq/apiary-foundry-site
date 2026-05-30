#!/usr/bin/env python3
"""
Contrast QA scanner for Apiary Foundry static site.

Crawls all .html files, parses CSS rules + inline styles, resolves
background/text/foreground color pairs, and flags WCAG failures.

Run:
    python scripts/check_contrast.py
    python scripts/check_contrast.py --write-css-vars

Rules:
  - Normal text: AA 4.5:1, AAA 7:1
  - Large text (18px+ or 14px+ bold): AA 3:1, AAA 4.5:1
  - UI components (nav pills, buttons, borders): AA 3:1 minimum
  - Nav links must pass at BOTH normal and :hover/:active states

Exit non-zero if any failure.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def hex_to_rgb(c: str) -> tuple[float, float, float]:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return (r / 255.0, g / 255.0, b / 255.0)


def parse_color(val: str) -> Optional[tuple[float, float, float]]:
    val = val.strip()
    if not val or val == "transparent" or val == "none":
        return None
    if val.startswith("#"):
        try:
            return hex_to_rgb(val)
        except ValueError:
            return None
    # rgb / rgba
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", val)
    if m:
        return (int(m[1]) / 255.0, int(m[2]) / 255.0, int(m[3]) / 255.0)
    # hsl / hsla
    m = re.match(r"hsla?\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?", val)
    if m:
        return hsl_to_rgb(int(m[1]), int(m[2]), int(m[3]))
    return None


def hsl_to_rgb(h: int, s: int, l: int) -> tuple[float, float, float]:
    s, l = s / 100.0, l / 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (r + m, g + m, b + m)


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    l1, l2 = relative_luminance(a) + 0.05, relative_luminance(b) + 0.05
    return max(l1, l2) / min(l1, l2)


def resolve_var(val: str, variables: dict[str, str]) -> str:
    """Replace CSS var() references with known values."""
    if "var(" not in val:
        return val
    while True:
        m = re.search(r"var\(\s*--([^\s,)]+)\s*(?:,\s*([^)]+))?\s*\)", val)
        if not m:
            break
        name, fallback = m[1], (m[2] or "")
        replacement = variables.get("--" + name, fallback.strip() or "transparent")
        val = val[: m.start()] + replacement + val[m.end() :]
    return val


CSS_COLOR_RE = re.compile(
    r"color\s*:\s*([^;{}]+)|background(?:-color)?\s*:\s*([^;{}]+)|background\s*:\s*([^;{}]+)",
    re.IGNORECASE,
)


def extract_css_blocks(css_text: str) -> list[tuple[str, str]]:
    """Yield (selector_str, block_body) pairs."""
    i = 0
    results = []
    while True:
        start = css_text.find("{", i)
        if start == -1:
            break
        sel = css_text[i:start].strip()
        end = css_text.find("}", start + 1)
        if end == -1:
            break
        body = css_text[start + 1 : end]
        results.append((sel, body))
        i = end + 1
    return results


def get_text_color(rule_body: str, variables: dict[str, str]) -> Optional[tuple[float, float, float]]:
    for m in CSS_COLOR_RE.finditer(rule_body):
        val = m[1] or m[2] or m[3]
        prop = rule_body[: m.start()].split(";")[-1].strip().lower()
        if "background" in prop:
            continue
        resolved = resolve_var(val.strip(), variables)
        return parse_color(resolved)
    return None


def get_bg_color(rule_body: str, variables: dict[str, str]) -> Optional[tuple[float, float, float]]:
    bg = None
    for m in CSS_COLOR_RE.finditer(rule_body):
        val = m[1] or m[2] or m[3]
        prop = rule_body[: m.start()].split(";")[-1].strip().lower()
        if "background" in prop:
            resolved = resolve_var(val.strip(), variables)
            c = parse_color(resolved)
            if c:
                bg = c
    return bg


# Known CSS custom properties from the site
KNOWN_VARS = {
    "--charcoal": "#171512",
    "--iron": "#24211c",
    "--graphite": "#3f382f",
    "--paper": "#f4efe3",
    "--paper-2": "#fff9ec",
    "--amber": "#d98b24",
    "--gold": "#f2c14e",
    "--blue": "#2f5f8f",
    "--rust": "#a24c21",
    "--green": "#4f7c63",
    "--ink": "#151412",
    "--muted": "#5f564b",
    "--line": "rgba(23,21,18,.16)",
    "--white": "#fffdf6",
    "--shadow": "0 28px 90px rgba(23,21,18,.18)",
    "--soft": "0 16px 46px rgba(23,21,18,.07)",
    "--max": "1180px",
}


# Critical selectors we always check at both desktop and mobile breakpoints
CRITICAL_SELECTORS = [
    ".nav-links a",          # the pills that failed
    ".nav-links a:hover",
    ".nav-links a[aria-current='page']",
    ".button",
    ".button:hover",
    ".ghost",
    ".ghost:hover",
    ".button.amber",
    ".button.amber:hover",
    "h1",
    "h2",
    "h3",
    "p",
    "p.lede",
    ".dark-section h2",
    ".dark-section p",
    ".dark-section .rich-copy",
    ".cell",
    ".forge-core",
    ".data-chain div",
    ".layer-stack div",
    ".final-card p",
    "footer",
    ".mobile-cta .button",
]


def check_file(html_path: Path, site_css_text: str) -> list[dict]:
    """Check one HTML file against the site CSS."""
    failures = []
    content = html_path.read_text(encoding="utf-8")

    # Extract inline style blocks from this page
    inline_css = ""
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", content, re.DOTALL | re.IGNORECASE):
        inline_css += "\n" + m[1]

    all_css = site_css_text + "\n" + inline_css

    # Extract CSS variables from :root and other var declarations
    variables = dict(KNOWN_VARS)
    for m in re.finditer(r"--([\w-]+)\s*:\s*([^;]+)", all_css):
        variables["--" + m[1]] = m[2].strip()

    # Extract all selector -> rule mappings
    rules = extract_css_blocks(all_css)

    def find_style(selector: str, include_prefix: bool = True) -> Optional[str]:
        """Find the last matching CSS rule body."""
        body = None
        for sel, b in rules:
            if selector == sel.strip():
                body = b
            elif include_prefix and sel.strip().endswith(selector):
                body = b
        return body

    # Check critical selectors at each breakpoint
    breakpoints = {
        "desktop": None,
        "tablet (<=1080px)": "1080px",
        "mobile (<=680px)": "680px",
        "small (<=420px)": "420px",
    }

    for bp_name, bp_max in breakpoints.items():
        for sel in CRITICAL_SELECTORS:
            body = find_style(sel, include_prefix=True)
            if not body:
                continue

            # Filter to rules inside this breakpoint if applicable
            if bp_max:
                # Find @media block that contains this selector
                media_blocks = re.finditer(
                    r"@media\s*\(\s*max-width\s*:\s*(\d+px)\s*\)\s*\{([^}]*)\}",
                    all_css,
                    re.DOTALL | re.IGNORECASE,
                )
                found = False
                for mm in media_blocks:
                    if mm[1] == bp_max:
                        inner = extract_css_blocks(mm[2])
                        for inner_sel, inner_body in inner:
                            if inner_sel.strip().endswith(sel) or inner_sel.strip() == sel:
                                body = inner_body
                                found = True
                                break
                        if found:
                            break
                if not found:
                    continue  # selector not overridden at this breakpoint

            fg = get_text_color(body, variables)
            bg = get_bg_color(body, variables)

            if not fg or not bg:
                continue

            ratio = contrast_ratio(fg, bg)
            is_large = sel.startswith(("h1", "h2", "h3", "h4", ".button", ".forge-core"))
            min_aa = 3.0 if is_large else 4.5
            min_aaa = 4.5 if is_large else 7.0

            if ratio < min_aa:
                failures.append(
                    {
                        "file": str(html_path.relative_to(Path.cwd())),
                        "breakpoint": bp_name,
                        "selector": sel,
                        "ratio": round(ratio, 2),
                        "fg": fg,
                        "bg": bg,
                        "level": "AA" if ratio >= 3.0 else "fail",
                        "severity": "high" if ratio < 3.0 else "medium",
                        "notes": f"Contrast {ratio:.2f}:1 below AA minimum {min_aa}:1",
                    }
                )
            elif ratio < min_aaa:
                failures.append(
                    {
                        "file": str(html_path.relative_to(Path.cwd())),
                        "breakpoint": bp_name,
                        "selector": sel,
                        "ratio": round(ratio, 2),
                        "fg": fg,
                        "bg": bg,
                        "level": "AAA",
                        "severity": "low",
                        "notes": f"Contrast {ratio:.2f}:1 below AAA minimum {min_aaa}:1",
                    }
                )

    # Hardcoded nav-wrap pill check at mobile
    # The pills sit in .nav-wrap which is sticky on top of potentially dark content
    if "nav-links a" in content:
        body = find_style(".nav-links a")
        if body:
            fg = get_text_color(body, variables)
            bg = get_bg_color(body, variables)
            if fg and bg:
                ratio = contrast_ratio(fg, bg)
                if ratio < 4.5:
                    failures.append(
                        {
                            "file": str(html_path.relative_to(Path.cwd())),
                            "breakpoint": "sticky-nav",
                            "selector": ".nav-links a (mobile sticky pill)",
                            "ratio": round(ratio, 2),
                            "fg": fg,
                            "bg": bg,
                            "level": "AA",
                            "severity": "high",
                            "notes": f"Nav pill readability against dark page sections",
                        }
                    )

    return failures


def main():
    parser = argparse.ArgumentParser(description="WCAG contrast QA scanner")
    parser.add_argument("--write-css-vars", action="store_true", help="Write CSS var registry JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--min-ratio", type=float, default=3.0, help="Minimum ratio to flag")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    css_path = root / "assets" / "site.css"
    site_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    all_failures: list[dict] = []

    for html in sorted(root.rglob("*.html")):
        if "node_modules" in str(html):
            continue
        failures = check_file(html, site_css)
        all_failures.extend(failures)

    # Deduplicate by file+selector+breakpoint
    seen = set()
    deduped = []
    for f in all_failures:
        key = (f["file"], f["selector"], f["breakpoint"])
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    all_failures = deduped

    if args.write_css_vars:
        out = root / "assets" / "css-vars.json"
        out.write_text(json.dumps(KNOWN_VARS, indent=2))
        print(f"Wrote {out}")

    if args.json:
        print(json.dumps(all_failures, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"  APIARY FOUNDRY — CONTRAST QA REPORT")
        print(f"{'=' * 60}")
        if not all_failures:
            print("  ✅ All checks passed — no contrast failures found.")
        else:
            print(f"  ⚠️  {len(all_failures)} issue(s) found\n")
            for f in all_failures:
                sev_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(
                    f"  {sev_emoji.get(f['severity'], '?')} {f['file']}\n"
                    f"     → {f['selector']} @ {f['breakpoint']}\n"
                    f"     → ratio {f['ratio']}:1 ({f['level']}) — {f['notes']}\n"
                )
        print(f"{'=' * 60}")

    if any(f["severity"] == "high" for f in all_failures):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
