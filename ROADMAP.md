# ROADMAP.md — Development Roadmap

Open work only; completed items are removed as they land (see git history).

---

## Production Errors

Found by `manage.py errordigest` over the August 2026 journal. Add each URL to
`smoketest` as it is fixed.

- [ ] `NoReverseMatch: city_detail with ('',)` — a stadium with an empty city slug; `/places/cities/`, `/places/stadiums/treveskyn-field/`, `/places/stadiums/rhodes-field/` (~12/week)
- [ ] `AttributeError: 'NoneType' object has no attribute 'games_played'` — `/places/stadiums/<slug>/`, `/bios/<slug>/games/` (281 in August)
- [ ] `KeyError: 'team'` / `'player'` / `'stadium'` — `/bios/<slug>/`, `/teams/<slug>/games/` (~30 in August)
- [ ] `RuntimeError: No active exception to reraise` — `/c/`
- [ ] Worker timeouts on `/sources/24/` and `/sources/33/` — some query there runs past gunicorn's 30s; ~10/week

## Deferred

- The error digest and the contact form both need `EMAIL_HOST_PASSWORD` (a Gmail app password for chris@soccerstats.us) in bert's `.env`. Until then the digest prints to its own journal and `/contact/` 500s with `SMTPSenderRefused`.
