# ROADMAP.md — Development Roadmap

Open work only; completed items are removed as they land (see git history).

---

## Deferred

- The error digest and the contact form both need `EMAIL_HOST_PASSWORD` (a Gmail app password for chris@soccerstats.us) in bert's `.env`. Until then the digest prints to its own journal and `/contact/` 500s with `SMTPSenderRefused`.
