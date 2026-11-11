# docs

Service notes for the site that used to live outside the repository.

- [domain-setup.md](domain-setup.md) — how the `hice.agency` domain (registered at Porkbun) is moved to Cloudflare DNS and attached to the `website` Worker as a custom domain. In Russian. No credentials inside: logins for Porkbun and Cloudflare are kept by the account owner, not here.

## What is deliberately not in the repository

- Original client screenshots, slides and the full PDF presentation that were used as sources for the case pages. They are not anonymised, so they stay out of this public repo. The site only uses the anonymised, redrawn versions in `assets/cases/`.
- The original (non-anonymised) Control Tower case write-up. Its anonymised version is in `data/cases.json`.
- Preview screenshots of the site taken while building the case pages. They can be regenerated from the live site at any time.

## Hosting in short

- The site is static and deployed as a Cloudflare Worker named `website` (config in `wrangler.jsonc`, static assets from the repo root).
- After changing `data/cases.json`, run `python3 build.py` and commit the generated HTML.
- When moving to another Cloudflare or GitHub account, the Worker has to be re-created (or re-connected to the repo) under the new account and the custom domains from `domain-setup.md` re-attached.
