# Apiary Foundry Site

Production marketing site for Apiary Foundry.

## Source inputs

- Seven design mockup: `/Users/bot/.hermes/profiles/seven/artifacts/apiary-foundry-website-2026-05-11/index.html`
- Jameela copy draft: `/Users/bot/.hermes/profiles/jameela/drafts/apiary-foundry-website-copy-v0.md`

## Local checks

```bash
python3 scripts/check_site.py
python3 -m http.server 4173
```

## Container

```bash
docker build -t apiary-foundry-site:local .
docker run --rm -p 8080:8080 apiary-foundry-site:local
```

## Deployment

- Production: `https://apiaryfoundry.com`, `https://www.apiaryfoundry.com`
- Staging: `https://staging.apiaryfoundry.com`
- Runtime target: existing Hetzner host `lexy-hetzner-01`
- Edge: existing Caddy container on the Hetzner box
