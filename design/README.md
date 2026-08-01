# Apiary Foundry design-system package

This directory preserves the implementation-facing material from the Willie-approved Apiary Foundry design package.

## Source and integrity

- Source: [Google Drive design kit](https://drive.google.com/file/d/1jldby1TNWgEyi3JNiHGdhyTogt6b2RJr/view?usp=sharing)
- Verified ZIP SHA-256: `4d85ed63b551f53d2278b6a737e2a3672ef9db936ff97a029bd7f4e8526d24d5`
- Imported design-system version: `0.1.0`

## Repository source of truth

1. `PRODUCT.md` — brand register, audience, purpose, personality, anti-references, and strategic principles.
2. `DESIGN.md` — canonical visual rules and implementation boundaries.
3. `design/apiary-foundry-design-tokens.json` — machine-readable tokens from the approved package.
4. `design/apiary-foundry-tokens.css` — package token utilities.
5. `assets/brand/` — production logo, mark, favicon, pattern, and runtime-token assets.

The large raster concept boards remain in the original Drive package. They are intentionally not committed because they are directional references containing generated text/geometry, not production source files.

## Deep-dive decisions

- The supplied SVG lockups are production starters and replace the old hand-coded nested-hex mark on the site. They are not final trademark vectors; large-format and registration use still requires a human vector pass.
- The site uses the light horizontal lockup on light navigation and the dark lockup on coal surfaces. The compact mark is reserved for favicon and constrained mobile signatures.
- The master site does not adopt the law-firm vertical concept. Legal documents, courtroom queues, and attorney-specific imagery remain isolated to a future vertical treatment.
- The new visual lane is **operator field manual**: cream paper, coal ink, restrained honey routes, condensed display type, technical annotations, and diagrams that expose operating mechanics.
- Decorative honeycomb geometry is limited to brand marks, process nodes, subtle corner texture, and small emphasis. It must not become a full-page bee motif.
- Existing lead capture, attribution, consent, Mautic, booking, semantic HTML, reduced motion, and responsive behavior are implementation invariants.

## Pushback / unresolved brand decisions

The kit explicitly leaves final bee anatomy, wordmark drawing, paper-texture intensity, UI distress, legal sub-branding, and long-term founder photography open. This rollout uses the supplied safe defaults without pretending those open items are settled. Any future change to those decisions must update `DESIGN.md` and the token files in the same PR.
