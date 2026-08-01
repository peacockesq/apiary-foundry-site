# Apiary Foundry Design System

> **Source:** Willie-approved package from Google Drive (`1jldby1TNWgEyi3JNiHGdhyTogt6b2RJr`)
> **Verified package SHA-256:** `4d85ed63b551f53d2278b6a737e2a3672ef9db936ff97a029bd7f4e8526d24d5`
> **Repository role:** Visual source of truth. `PRODUCT.md` controls strategy and voice; this file controls visual implementation.
> **Status:** Working design direction, version 0.1.0
> **Primary implementation rule:** Read this file before making any visual change. Use the supplied tokens and assets. Do not invent new colors, logo geometry, type styles, or illustration styles without updating this document.

## 1. Brand premise

Apiary Foundry is an **operator-led growth systems** company. It combines deterministic infrastructure, AI-assisted execution, and human judgment to remove bottlenecks and make growth measurable.

The visual system should feel:

- **Operator-built, not agency-polished:** credible, practical, and slightly industrial.
- **Technical without becoming sterile:** diagrams, systems, routes, measurement, and visible mechanics.
- **Editorial rather than “AI neon”:** cream paper, black ink, honey gold, strong typography, and hand-rendered sketch work.
- **Confident but skeptical:** the brand is pro-AI and anti-theater.
- **Human-led:** machines do the heavy lifting; judgment decides what deserves to exist.

### Master-brand boundary

Apiary Foundry is broader than legal technology. Do **not** make every master-brand page look law-firm-specific. Law firms may use a dedicated vertical treatment with documents, courts, attorneys, and legal workflows, but the core brand must also support marketing systems, analytics, CRM, lifecycle, software, and operations.

## 2. Core message hierarchy

1. **Outcome:** measurable growth and increased throughput.
2. **Method:** remove constraints, connect systems, and automate accountable work.
3. **Architecture:** deterministic systems + AI agents + human strategy.
4. **Proof:** operator experience, measurable economics, and functioning systems.
5. **Personality:** candid, technically curious, occasionally funny, never inflated.

Useful language:

- The cure for random acts of marketing.
- Systems before spend.
- Stop funding motion. Fund what works.
- Remove constraints. Unlock throughput. Multiply results.
- The machine accelerates the work. Human strategy decides what is worth doing.

Avoid:

- “Revolutionary,” “cutting-edge,” “game-changing,” or generic AI hype.
- Bees/hives used as cute puns in every sentence.
- Claims that imply full autonomy where review still matters.
- A sleek cyberpunk/SaaS aesthetic disconnected from the operator story.

## 3. Visual concept

The design language combines four materials:

1. **Ink:** coal-black typography, linework, diagrams, and heavy panels.
2. **Paper:** warm cream editorial backgrounds with extremely subtle grain.
3. **Honey:** restrained gold used for emphasis, route lines, buttons, data, and key words.
4. **Blueprint/sketch:** black-and-white technical or editorial illustrations with selective gold marks.

The site should look like a field manual produced by an unusually capable operator—not a generic automation landing page.

## 4. Logos

### Supplied variants

- `assets/brand/logos/logo-horizontal-light.svg`
- `assets/brand/logos/logo-horizontal-dark.svg`
- `assets/brand/logos/logo-stacked-light.svg`
- `assets/brand/logos/mark-light.svg`
- `assets/brand/logos/mark-dark.svg`
- `assets/brand/logos/favicon.svg`

### Logo rules

- Use the horizontal lockup in primary navigation and wide footers.
- Use the stacked lockup for square collateral, proposals, and occasional hero moments.
- Use the hexagonal bee mark for avatars, favicons, UI badges, and small brand signatures.
- Maintain clear space equal to at least one bee-head diameter on every side.
- Never stretch, bevel, glow, emboss, or place the logo over a busy illustration.
- The gold offset edge may appear on the hexagon, but avoid gradients inside the core production logo.
- Generated logo sheets in `/references` are **concept references**, not production source files.

### Production warning

The SVGs are clean implementation starters, but the final bee geometry and wordmark should receive a human vector pass before trademark filing, large-format printing, or permanent brand registration. AI-generated raster logo text should never be used as the canonical logo.

## 5. Color system

| Token | Hex | Use |
|---|---:|---|
| Coal | `#0F0F10` | Primary text, dark panels, navigation |
| Charcoal | `#1A1A1C` | Secondary dark surfaces |
| Slate | `#2B2B2E` | Borders, muted dark cards |
| Graphite | `#515154` | Muted text on light backgrounds |
| Cream | `#F6F1E8` | Primary page background |
| Paper | `#FBF8F1` | Raised light surfaces |
| White | `#FFFFFF` | High-contrast text and UI |
| Honey | `#E0A21C` | Primary accent and CTAs |
| Amber | `#F5C24D` | Hover/highlight state |
| Ochre | `#B8750A` | Accessible gold text on light surfaces |
| Success | `#2E7D52` | Positive system status |
| Warning | `#D58A00` | Delays and attention |
| Danger | `#B83A32` | Errors only |

### Color rules

- Gold should occupy roughly **5–12%** of a typical page, not half the screen.
- Never use honey gold for long body copy on cream. Use ochre or coal. For small warm labels that must retain the field-manual accent, use the site-derived deep amber `#8C4F00` (5.77:1 on cream), never the lighter ochre.
- Use dark panels for emphasis, proof, warnings, calls to action, and data—not every section.
- Avoid gradients except subtle photographic overlays or a restrained honey-to-amber CTA fill.

## 6. Typography

### Families

- **Display:** Oswald, with Impact/Arial Narrow fallbacks.
- **Body/UI:** Inter, with system sans fallbacks.
- **Data/code:** IBM Plex Mono, with system monospace fallbacks.

### Hierarchy

- Display headlines: uppercase or title case, condensed, 700 weight, tight leading (`0.92–1.0`).
- Body copy: 400–500 weight, `1.55–1.72` line height, maximum reading width `46rem`.
- Kicker labels: small uppercase, 700–800 weight, widened tracking, ochre or honey.
- Numeric proof: large condensed numerals, short supporting label.

### Editorial rule

Use uppercase for short impact language. Do not put paragraph-length copy in uppercase. Highlight one short phrase in honey; do not alternate colors word by word.

## 7. Layout and spacing

- Maximum content width: `80rem`.
- Reading width: `46rem`.
- Desktop grid: 12 columns with `2rem` gutters.
- Mobile gutters: `1rem`.
- Base spacing unit: `4px`; preferred jumps are 8, 12, 16, 24, 32, 48, 64, and 96px.
- Section padding: 64–112px desktop, 48–72px mobile.
- Use asymmetry deliberately: editorial text block paired with sketch, diagram, data card, or dark callout.
- Avoid endless center-aligned SaaS sections.

## 8. Surfaces and borders

- Default surface: warm paper with subtle dot/grain texture.
- Dark surface: coal with very light grain; never pure glossy black.
- Borders: 1px coal at 14–20% opacity on light surfaces; honey edge for active/featured states.
- Corners: mostly 2–6px. This is not a pill-heavy brand.
- Hexagons are reserved for marks, process nodes, icon frames, and small emphasis objects.
- Shadows: sparse and ink-like, not soft floating-dashboard shadows.

## 9. Illustration style

### Canonical style

Black-and-white editorial pen, engraving, or technical-sketch art with selective honey-gold accents. Subjects should look hand-rendered but retain clear operational meaning.

Good subjects:

- workflow queues and bottlenecks;
- operators at desks or control points;
- conveyors, gears, robotic arms, routing arrows, clocks, stacks, dashboards;
- bees used as system-builders or brand signatures;
- diagrams that expose hidden process mechanics;
- before/after operational contrast.

Avoid:

- cute cartoon bees;
- generic humanoid robots shaking hands;
- glowing brains, neon circuits, or blue holograms;
- photorealistic law-firm stock imagery;
- diagrams with illegible generated text.

### Image-generation prompt base

> Black-and-white editorial ink sketch and technical infographic for Apiary Foundry, warm cream paper background, coal-black linework, selective honey-gold accents, restrained honeycomb geometry, practical operational systems, visible workflow mechanics, slightly imperfect hand-rendered texture, premium business publication aesthetic, high contrast, ample negative space, no neon, no blue cyberpunk, no generic humanoid robot, no illegible microtext.

For production graphics, generate **art without critical text**, then typeset the text in HTML, Figma, Canva, or a layout tool.

## 10. Iconography

- Use simple monoline or solid black symbols inside thin hexagonal frames.
- Stroke width should remain visually consistent at 16, 24, and 32px sizes.
- Gold may identify active state or the route through a system.
- Every icon must still be understandable in monochrome.
- Do not mix rounded consumer-app icons with technical line art.

## 11. Core components

### Buttons

**Primary:** honey fill, coal text, 1px coal border, slight upward movement on hover.
**Dark:** coal fill, white text, optional honey arrow.
**Outline:** transparent/paper fill, coal border and text.
Avoid pill shapes. Use direct labels: “Start the audit,” “See the system,” “Book a strategy call.”

### Cards

- Light card: paper surface, thin coal border, 6px radius.
- Dark card: coal surface, honey or slate edge.
- Include a clear label, one useful statement, and optional proof/action.
- Avoid decorative card grids that contain no decision-making value.

### Stats

- Hex icon or compact mark.
- Large number.
- One-line interpretation.
- Optional source/method note.

### Process diagrams

- 3–5 nodes maximum per visible row.
- Use honey to show the path and coal for stable infrastructure.
- Show queues, review points, and failure loops honestly.
- Human review should be visually explicit where it exists.

### Callouts

- **Constraint alert:** dark surface, warning triangle/clock, direct operational statement.
- **Outcome callout:** honey surface, black upward-trend or throughput icon.
- **Field note:** cream surface with black rule and bee signature.

### Forms

- Labels above fields; never placeholder-only.
- Large click/tap targets.
- Coal text on paper, visible focus ring in honey plus coal outline.
- Ask only for data necessary to route or qualify the user.

## 12. Page patterns

### Homepage

1. Operator-led positioning and sharp outcome headline.
2. Three-layer architecture: deterministic systems / AI agents / human strategy.
3. Proof and operating results.
4. What AF builds.
5. Five Hives.
6. Operator story.
7. Audit CTA and field notes signup.

### Service page

1. Business constraint.
2. Economic consequence.
3. System diagram.
4. What gets built.
5. Human/AI responsibility split.
6. Measurement plan.
7. Proof.
8. Engagement CTA.

### Insight/article page

- Strong editorial headline.
- Narrow reading column.
- Sketch/diagram that explains the thesis.
- Dark pull-quote or operational rule.
- Practical checklist or model.
- Low-pressure audit or newsletter CTA.

### Law-firm vertical variant

Permitted imagery includes court queues, documents, attorney review, client communications, source-document extraction, and administrative follow-up. Keep master tokens unchanged; only the content and illustrations become legal-specific.

## 13. Voice and UI copy

Voice is direct, candid, curious, operational, and willing to say when a tool does not solve the actual problem.

Preferred:

- “Work piles up here.”
- “This is the constraint.”
- “Automate the queue, not the theater.”
- “Human review stays here because the judgment matters.”
- “What gets measured gets funded.”

Avoid:

- “Leverage next-generation AI to unlock synergistic efficiencies.”
- excessive bee metaphors;
- anonymous corporate “we” without operator accountability;
- certainty where the system is experimental.

## 14. Accessibility

- Target WCAG 2.2 AA.
- Never use gold alone to communicate state.
- Provide text alternatives for every meaningful sketch or process graphic.
- Maintain visible keyboard focus.
- Honor reduced-motion preferences.
- Use semantic headings and landmarks.
- Do not place body text over textured illustration areas.
- Test color contrast rather than trusting the palette concept board.

## 15. Motion

Motion should explain process:

- route line draws;
- queue advances;
- node activates;
- metric increments;
- review gate opens.

Keep duration between 120–320ms for UI interactions. Avoid perpetual floating, buzzing, or decorative bee animation. One restrained brand animation is enough.

## 16. AI implementation rules

Any coding or design agent working on Apiary Foundry should follow these rules:

1. Read `PRODUCT.md`, `DESIGN.md`, `design/apiary-foundry-design-tokens.json`, and `design/apiary-foundry-tokens.css` first.
2. Reuse supplied tokens; do not sample colors from raster concept sheets.
3. Use SVG assets from `/assets`, not logos embedded in generated PNGs.
4. Treat `/references` as inspiration, not a source of production text or exact geometry.
5. Do not make the master site law-firm-only.
6. Do not add fake client logos, metrics, testimonials, or case-study claims.
7. Do not replace direct copy with generic AI marketing language.
8. Render critical wording as HTML text, not inside generated imagery.
9. Preserve accessibility and responsive behavior.
10. When a new visual rule is introduced, update this file and the token files in the same change.

## 17. Recommended repository structure

```text
/design.md
/design-tokens.json
/tokens.css
/assets/
  /logos/
  /patterns/
  /illustrations/
  /icons/
/references/
/components/
/app-or-site-source/
```

## 18. Open design decisions

These require a human decision before full rollout:

- Final bee anatomy and hexagon geometry.
- Whether the wordmark stays geometric Inter or receives a custom-drawn type treatment.
- Exact paper texture strength.
- Degree of rough ink distress in UI panels.
- Whether law-firm consulting receives a sub-brand or remains a service page.
- Final photography strategy for Willie/operator imagery.

## 19. Definition of “on brand”

A design is on brand when it can answer yes to all five:

1. Does it expose how the system works?
2. Does it communicate a measurable business outcome?
3. Does it feel operator-built rather than hype-built?
4. Is AI shown as accountable infrastructure rather than magic?
5. Could the piece work in monochrome with gold removed?
