# ROADMAP.md — Development Roadmap

Open work only; completed items are removed as they land (see git history).

---

## Competitions

- [ ] Normalize original NASL postseason data: connect playoff seasons in the UI, move playoff games out of the main league seasons, and resolve the incomplete 1975–1983 split (including the extra 1976 and 1981 games). The 1968, 1970–1974, and 1984 playoffs are currently stored entirely in the league season; 1969 had no playoffs.

## Deferred

- The error digest and the contact form both need `EMAIL_HOST_PASSWORD` (a Gmail app password for chris@soccerstats.us) in bert's `.env`. Until then the digest prints to its own journal and `/contact/` 500s with `SMTPSenderRefused`.
