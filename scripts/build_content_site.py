#!/usr/bin/env python3
"""Build Apiary Foundry static pages from the approved markdown content package."""
from __future__ import annotations

import html
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONTENT_DIR = Path('/Users/bot/.openclaw/workspace/projects/apiary-foundry/content')
CONTENT_DIR = Path(os.environ.get('APIARY_CONTENT_DIR', DEFAULT_CONTENT_DIR))
ROOT = Path(__file__).resolve().parents[1]

PAGE_FILES = [
    '01-home.md',
    '02-about-willie-peacock.md',
    '03-measurement-engine.md',
    '04-growth-os.md',
    '05-five-hives-overview.md',
    '06-acquisition-hive.md',
    '07-content-search-hive.md',
    '08-conversion-hive.md',
    '09-lifecycle-hive.md',
    '10-measurement-hive.md',
    '11-proof-case-studies.md',
    '12-work-with-us.md',
]

OLD_DIRS = [
    'growth-strategy', 'acquisition', 'conversion', 'content-seo', 'lifecycle',
    'measurement-compliance', 'about', 'case-studies'
]

NAV = [
    ('/', 'Home'),
    ('/measurement-engine/', 'Measurement Engine'),
    ('/growth-os/', 'Growth OS'),
    ('/five-hives/', 'Five Hives'),
    ('/about-willie-peacock/', 'Willie'),
    ('/proof/', 'Proof'),
    ('/blog/', 'Blog'),
    ('/work-with-us/', 'Work With Us'),
]

ASSET_VERSION = '20260513-mobile'
MAUTIC_HEAD = '''  <script>
    (function(w,d,t,u,n,a,m){w['MauticTrackingObject']=n;w[n]=w[n]||function(){(w[n].q=w[n].q||[]).push(arguments)},a=d.createElement(t),m=d.getElementsByTagName(t)[0];a.async=1;a.src=u;m.parentNode.insertBefore(a,m)})(window,document,'script','https://mautic.apiaryfoundry.com/mtc.js','mt');
    mt('send', 'pageview');
  </script>'''

NEWSLETTER_STRIP = '''<section class="newsletter-strip container" aria-label="Apiary Foundry newsletter"><div><p class="eyebrow">Field notes</p><h2>Get measurable growth notes.</h2><p>Tracking, lead capture, attribution, lifecycle, and AI-assisted operations. Useful, not ornamental.</p></div><form class="lead-form compact newsletter-form" data-apiary-lead-form data-source-form="footer_newsletter" data-event-name="newsletter_signup" data-form-location="global-footer"><label>Email<input name="email" type="email" autocomplete="email" placeholder="you@company.com" required /></label><label class="checkbox full"><input name="marketing_consent" type="checkbox" value="yes" checked /><span data-consent-text>I agree to receive Apiary Foundry field notes and marketing communications. I can opt out later.</span></label><button class="button amber" type="submit">Subscribe</button><p class="form-status" data-form-status role="status" aria-live="polite"></p></form></section>'''

DIAGNOSTIC_FORM = '''<section class="container final-section" id="diagnostic"><div class="final-card lead-card"><div><p class="eyebrow">Work with Apiary Foundry</p><h2>Start with the system, not the pitch.</h2><p>If the team is busy and the scoreboard is still suspect, bring the system into focus.</p><p class="form-note">Submissions route through the Apiary automation layer into Mautic. No browser-side CRM secrets. No nonsense.</p></div><form class="lead-form" id="apiary-growth-diagnostic" data-apiary-lead-form data-source-form="growth_diagnostic" data-event-name="growth_diagnostic_requested" data-form-location="work-with-us-final"><label>Name<input name="name" autocomplete="name" placeholder="Your name" /></label><label>Email<input name="email" type="email" autocomplete="email" placeholder="you@company.com" required /></label><label class="full">Where is the system leaking?<textarea name="message" rows="4" placeholder="Tracking, paid media, landing pages, lifecycle, reporting, speed-to-lead..."></textarea></label><label class="checkbox full"><input name="marketing_consent" type="checkbox" value="yes" /><span data-consent-text>I agree to receive follow-up and marketing communications from Apiary Foundry. I can opt out later.</span></label><button class="button amber" type="submit">Send diagnostic request</button><p class="form-status" data-form-status role="status" aria-live="polite"></p></form></div></section>'''

CTA_MAP = {
    'Build the measurement engine': '/measurement-engine/',
    'See the five hives': '/five-hives/',
    'Explore the Five Hives': '/five-hives/',
    'Meet Willie': '/about-willie-peacock/',
    'Start with a growth system audit': '/work-with-us/',
    'Build the operating layer': '/growth-os/',
    'Make the scoreboard trustworthy': '/measurement-engine/',
    'Make spend answerable': '/paid-media-acquisition/',
    'Build content that has a job': '/seo-content-marketing/',
    'Turn traffic into evidence': '/conversion-rate-optimization/',
    'Protect the value of every lead': '/lifecycle-crm/',
    'Build measurement the business can trust': '/marketing-measurement-attribution/',
    'Bring proof into the system': '/proof/',
    'Stop guessing which work deserves money': '/work-with-us/',
    'Build the Measurement Engine': '/work-with-us/',
    'Design the Growth OS': '/work-with-us/',
    'Explore Acquisition Hive': '/paid-media-acquisition/',
    'Explore Content & Search Hive': '/seo-content-marketing/',
    'Explore Conversion Hive': '/conversion-rate-optimization/',
    'Explore Lifecycle Hive': '/lifecycle-crm/',
    'Explore Measurement Hive': '/marketing-measurement-attribution/',
    'Build the Content & Search Hive': '/work-with-us/',
    'Build the Lifecycle Hive': '/work-with-us/',
    'Audit acquisition': '/work-with-us/',
    'Audit conversion': '/work-with-us/',
    'Audit measurement': '/work-with-us/',
    'Work with Willie': '/work-with-us/',
    'Start the conversation': '#diagnostic',
}

@dataclass
class Page:
    source: Path
    title: str
    slug: str
    meta_title: str
    meta_description: str
    body_lines: list[str]


def slug_to_dir(slug: str) -> Path:
    clean = slug.strip('` ').strip()
    if clean == '/':
        return ROOT
    return ROOT / clean.strip('/')


def parse_page(path: Path) -> Page:
    lines = path.read_text().splitlines()
    title = lines[0].lstrip('# ').strip()
    slug = '/'
    meta_title = title
    meta_description = ''
    body_start = 1
    for i, line in enumerate(lines[1:], start=1):
        if line.startswith('Slug:'):
            slug = line.split(':', 1)[1].strip().strip('`')
            body_start = i + 1
        elif line.startswith('Meta title:'):
            meta_title = line.split(':', 1)[1].strip()
            body_start = i + 1
        elif line.startswith('Meta description:'):
            meta_description = line.split(':', 1)[1].strip()
            body_start = i + 1
        elif line.startswith('## ') or line.startswith('# '):
            body_start = i
            break
    return Page(path, title, slug, meta_title, meta_description, lines[body_start:])


def inline_md(text: str) -> str:
    replacements = {
        'The tracking discipline that made Google reps speechless.': 'The tracking discipline that made platform accountability measurable.',
        'The AF lesson:': 'The Apiary Foundry lesson:',
        'Start with a Growth System Audit': 'Start with a growth system audit',
    }
    text = replacements.get(text, text)
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def split_sections(lines: list[str]):
    sections = []
    current = {'level': 0, 'heading': '', 'lines': []}
    for raw in lines:
        line = raw.rstrip()
        if line.startswith('# '):
            # Treat first H1 after Hero marker as hero heading, not a new body section.
            current['lines'].append(line)
        elif line.startswith('## '):
            if current['heading'] or current['lines']:
                sections.append(current)
            current = {'level': 2, 'heading': line[3:].strip(), 'lines': []}
        else:
            current['lines'].append(line)
    if current['heading'] or current['lines']:
        sections.append(current)
    return sections


def paragraphize(lines: list[str]) -> str:
    out = []
    in_ul = False
    promote_next_to_h3 = False
    for raw in lines:
        line = raw.strip()
        if not line:
            if in_ul:
                out.append('</ul>'); in_ul = False
            continue
        lower = line.lower()
        if lower.startswith('suggested visual') or lower.startswith('**suggested visual:**') or lower in {'### design note', '### story', '### system elements to highlight'}:
            continue
        if lower == '### working title':
            promote_next_to_h3 = True
            continue
        if line in {'Each AF case study should follow the same structure:', 'Recommended case study categories:'}:
            continue
        if 'This should be one of the strongest proof modules' in line or 'Treat this as founder-led credibility' in line:
            continue
        if promote_next_to_h3:
            if in_ul:
                out.append('</ul>'); in_ul = False
            out.append(f'<h3>{inline_md(line)}</h3>')
            promote_next_to_h3 = False
            continue
        if line.startswith('# '):
            if in_ul:
                out.append('</ul>'); in_ul = False
            out.append(f'<h1>{inline_md(line[2:].strip())}</h1>')
            continue
        if line.startswith('### '):
            if in_ul:
                out.append('</ul>'); in_ul = False
            out.append(f'<h3>{inline_md(line[4:].strip())}</h3>')
            continue
        if line.startswith('- '):
            if not in_ul:
                out.append('<ul>'); in_ul = True
            out.append(f'<li>{inline_md(line[2:].strip())}</li>')
            continue
        if line.startswith('>'):
            if in_ul:
                out.append('</ul>'); in_ul = False
            out.append(f'<blockquote>{inline_md(line.lstrip("> ").strip())}</blockquote>')
            continue
        if line.startswith('**CTA:**') or line.startswith('**Primary CTA:**') or line.startswith('**Secondary CTA:**'):
            if in_ul:
                out.append('</ul>'); in_ul = False
            label = re.sub(r'^\*\*(Primary CTA:|Secondary CTA:|CTA:)\*\*\s*', '', line).strip().rstrip('.')
            href = CTA_MAP.get(label, '/work-with-us/')
            out.append(f'<p class="inline-cta"><a class="button amber" href="{href}">{inline_md(label)}</a></p>')
            continue
        if in_ul:
            out.append('</ul>'); in_ul = False
        out.append(f'<p>{inline_md(line)}</p>')
    if in_ul:
        out.append('</ul>')
    return '\n'.join(out)


def nav_html(active: str) -> str:
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href.rstrip('/') == active.rstrip('/') else ''
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    return ''.join(links)


def hero_diagram(kind: str) -> str:
    if kind == '/':
        cells = [
            ('Acquisition', 'paid + demand'), ('Content', 'intent + voice'), ('Conversion', 'offer + proof'),
            ('Lifecycle', 'CRM + follow-up'), ('Measurement', 'truth + budget')
        ]
        return system_orb('Growth OS', 'operator-led', cells)
    if 'measurement-engine' in kind:
        return '''<div class="data-chain" aria-label="Measurement engine data path">
          <div>Ad click<small>gclid / fbclid</small></div><span></span><div>Landing page<small>UTM + form</small></div><span></span><div>CRM<small>stage + source</small></div><span></span><div>Warehouse<small>normalized truth</small></div><span></span><div>Dashboard<small>budget decision</small></div>
        </div>'''
    if 'growth-os' in kind:
        return '''<div class="layer-stack" aria-label="Growth OS layers">
          <div><b>Decision layer</b><small>what deserves funding</small></div><div><b>Measurement layer</b><small>truth and QA</small></div><div><b>Automation layer</b><small>robots protecting repeatable work</small></div><div><b>Execution layer</b><small>campaigns, pages, CRM, content</small></div><div><b>Strategy layer</b><small>economics, offer, audience</small></div>
        </div>'''
    if 'five-hives' in kind:
        return system_orb('Five hives', 'one system', [('Acquisition','fund demand'),('Content','earn intent'),('Conversion','prove offer'),('Lifecycle','protect leads'),('Measurement','fund winners')])
    return '''<div class="workbench-card" aria-label="Apiary workbench">
      <div class="workbench-top"><span>operator review</span><span>workflow QA</span></div>
      <div class="signal-bars"><i style="height:42%"></i><i style="height:66%"></i><i style="height:82%"></i><i style="height:54%"></i><i style="height:76%"></i></div>
      <p>Every page, workflow, and campaign has to produce a decision-ready signal.</p>
    </div>'''


def system_orb(title: str, subtitle: str, cells: list[tuple[str, str]]) -> str:
    cell_html = ''.join(f'<div class="cell c{i+1}">{html.escape(a)}<small>{html.escape(b)}</small></div>' for i, (a, b) in enumerate(cells))
    return f'''<aside class="schematic" aria-label="Apiary Foundry system diagram">
      <div class="schematic-inner"><div class="topline"><span>system route</span><span>operator controlled</span></div>
      <svg class="route" viewBox="0 0 540 360" preserveAspectRatio="none"><path d="M56 82 C145 38 214 122 270 162 S404 68 484 112 M80 278 C152 224 210 278 270 212 S382 292 462 224"/></svg>
      <div class="anno a1">source of truth</div><div class="anno a2">robots prevent decay</div><div class="anno a3">human judgment at center</div>
      <div class="forge-core">{html.escape(title)}<small>{html.escape(subtitle)}</small></div>{cell_html}</div>
    </aside>'''


def extract_hero(page: Page):
    lines = page.body_lines
    hero_start = 0
    for i, line in enumerate(lines):
        if line.strip() == '## Hero':
            hero_start = i + 1
            break
    hero_lines = []
    for line in lines[hero_start:]:
        if line.startswith('## ') and hero_lines:
            break
        if line.strip() and line.strip() != '## Hero':
            hero_lines.append(line)
    heading = page.title
    paras = []
    ctas = []
    for line in hero_lines:
        s = line.strip()
        if s.startswith('# '):
            heading = s[2:].strip()
            continue
        if s.startswith('**Primary CTA:**') or s.startswith('**Secondary CTA:**') or s.startswith('**CTA:**'):
            label = re.sub(r'^\*\*(Primary CTA:|Secondary CTA:|CTA:)\*\*\s*', '', s).strip().rstrip('.')
            ctas.append(label)
        elif s.lower().startswith('suggested visual') or s.lower().startswith('**suggested visual:**'):
            continue
        elif s:
            paras.append(s)
    if not ctas:
        ctas = ['Work with Apiary Foundry']
    return heading, paras, ctas


def render_page(page: Page) -> str:
    heading, paras, ctas = extract_hero(page)
    slug = page.slug if page.slug.endswith('/') else page.slug + '/'
    if page.slug == '/': slug = '/'
    sections = split_sections(page.body_lines)
    # Remove hero section from body cards.
    sections = [s for s in sections if s['heading'] != 'Hero']

    primary = ctas[0]
    secondary = ctas[1] if len(ctas) > 1 else 'See the five hives'
    primary_href = CTA_MAP.get(primary, '/work-with-us/')
    secondary_href = CTA_MAP.get(secondary, '/five-hives/')

    page_class = 'home' if page.slug == '/' else 'subpage'
    proof_band = ''
    if page.slug == '/':
        proof_band = '''<div class="founder-band"><div class="portrait-token">WP</div><div><p class="eyebrow">Operator credibility</p><h2>Led by Willie Peacock.</h2><p>Attorney, Chicago Booth MBA candidate, paid media and growth operator, and builder of measurement systems that preserve the data most teams lose.</p></div><div class="proof-chip"><b>Publisher</b><span>massive travel credit card affiliate growth and measurement buildout</span></div></div>'''

    body = []
    # Special doctrine band if content includes it.
    if page.slug == '/':
        body.append('<section class="doctrine"><div class="container"><p>What gets measured gets funded.</p></div></section>')

    structural_home_sections = {'Above-the-fold proof band', 'Doctrine section', 'Founder section', 'Closing CTA', 'Stop funding motion. Fund what works.'}
    rendered_sections = []
    for section in sections:
        if page.slug == '/' and section['heading'] in structural_home_sections:
            continue
        if section['heading'] == 'Design note':
            continue
        if page.slug == '/proof' and section['heading'] in {'Case study format', 'Placeholder for future client case studies'}:
            continue
        if not ''.join(section['lines']).strip() and section['heading'] in {'Doctrine section', 'Founder section', 'Closing CTA'}:
            continue
        rendered_sections.append(section)

    heading_map = {
        'Proof themes to use on this page': 'Proof themes',
        'Placeholder for future client case studies': 'Future case studies',
        'Case study format': 'How proof is structured',
        'Architecture overview': 'How the measurement engine carries data',
    }

    for idx, section in enumerate(rendered_sections):
        heading_html = inline_md(heading_map.get(section['heading'], section['heading']))
        content = paragraphize(section['lines'])
        if page.slug == '/work-with-us' and section['heading'] == 'Engagement models':
            content = '<div class="visual-break" aria-label="Apiary engagement flow"><span>Diagnose</span><span>Prioritize</span><span>Build</span></div>'
        if page.slug == '/five-hives' and section['heading'] == 'Hive 1: Acquisition':
            content = '<div class="visual-break" aria-label="Five hive operating flow"><span>Traffic</span><span>Conversion</span><span>Measurement</span></div>'
        mod = idx % 4
        if page.slug.startswith('/paid-media') or page.slug.startswith('/seo-content') or page.slug.startswith('/conversion') or page.slug.startswith('/lifecycle') or page.slug.startswith('/marketing-measurement'):
            cls = 'section-method' if section['heading'] in {'AF acquisition method','AF content method','AF conversion method','AF lifecycle method','AF measurement method'} else 'content-section'
        else:
            cls = ['content-section','split-section','panel-grid-section','dark-section'][mod]
        body.append(f'<section class="{cls}"><div class="container"><div class="section-kicker">{idx+1:02d}</div><h2>{heading_html}</h2><div class="rich-copy">{content}</div></div></section>')

    final_section = '<section class="container final-section"><div class="final-card"><div><p class="eyebrow">Work with Apiary Foundry</p><h2>Stop funding motion. Fund what works.</h2><p>If the team is busy and the scoreboard is still suspect, bring the system into focus.</p></div><div class="cta-stack"><a class="button amber" href="/work-with-us/">Start with a growth system audit</a><a class="ghost" href="/measurement-engine/">Build the measurement engine</a></div></div></section>'
    if page.slug == '/work-with-us':
        final_section = DIAGNOSTIC_FORM

    html_body = '\n'.join(body)
    lede = ''.join(f'<p class="lede">{inline_md(p)}</p>' for p in paras)
    hero = f'''<header class="hero container">
      <div class="hero-grid"><div><p class="eyebrow">Apiary Foundry / operator-led growth system</p><h1>{inline_md(heading)}</h1>{lede}
      <div class="hero-actions"><a class="button amber" href="{primary_href}">{inline_md(primary)}</a><a class="ghost" href="{secondary_href}">{inline_md(secondary)}</a></div></div>{hero_diagram(page.slug)}</div>{proof_band}</header>'''

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(page.meta_title)}</title>
  <meta name="description" content="{html.escape(page.meta_description)}" />
  <meta property="og:title" content="{html.escape(page.meta_title)}" />
  <meta property="og:description" content="{html.escape(page.meta_description)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://apiaryfoundry.com{page.slug if page.slug != '/' else '/'}" />
  <meta name="theme-color" content="#171512" />
  <link rel="canonical" href="https://apiaryfoundry.com{page.slug if page.slug != '/' else '/'}" />
  <link rel="preload" href="/assets/site.css?v={ASSET_VERSION}" as="style" />
  <link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}" />
{MAUTIC_HEAD}
</head>
<body class="{page_class}">
  <a class="skip" href="#main">Skip to content</a>
  <div class="nav-wrap"><nav class="container" aria-label="Primary navigation"><a class="brand" href="/" aria-label="Apiary Foundry home"><span class="mark" aria-hidden="true"><svg viewBox="0 0 64 64"><path fill="#d98b24" d="M32 4 52 16v24L32 60 12 40V16z"/><path fill="#171512" d="M32 14 43 21v14L32 46 21 35V21z"/><path fill="#f2c14e" d="M32 20 38 24v8l-6 6-6-6v-8z"/></svg></span><span>Apiary Foundry</span></a><div class="nav-links">{nav_html(slug)}</div><a class="button amber nav-cta" href="/work-with-us/">Start diagnostic</a></nav></div>
  <main id="main">{hero}{html_body}{final_section}</main>
{NEWSLETTER_STRIP}
  <footer class="container"><span>© 2026 Apiary Foundry.</span><span>The cure for random acts of marketing.</span></footer>
  <a class="button amber mobile-cta" href="/work-with-us/">Start diagnostic</a>
  <script src="/assets/apiary-lead-capture.js" defer></script>
</body>
</html>'''


def main():
    for old in OLD_DIRS:
        p = ROOT / old
        if p.exists():
            shutil.rmtree(p)
    for fname in PAGE_FILES:
        page = parse_page(CONTENT_DIR / fname)
        out_dir = slug_to_dir(page.slug)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(render_page(page))
    print(f'Built {len(PAGE_FILES)} pages from {CONTENT_DIR}')

if __name__ == '__main__':
    main()
