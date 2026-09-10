# ROADMAP.md — Development Roadmap

Open work only; completed items are removed as they land (see git history).

---

## Competitions

- [ ] Normalize original NASL postseason data: connect playoff seasons in the UI, move playoff games out of the main league seasons, and resolve the incomplete 1975–1983 split (including the extra 1976 and 1981 games). The 1968, 1970–1974, and 1984 playoffs are currently stored entirely in the league season; 1969 had no playoffs.
- [ ] Nine foreign guest clubs are recorded as NASL participants — Coventry City, Hertha BSC, Hapoel Tel Aviv, CF Monterrey and Varzim S.C. in 1970; Apollon Limassol, Bangu, Heart of Midlothian and Vicenza Calcio in 1971. They are the touring sides of the NASL's International Cup, filed under the league competition with no `round` to separate them: 24 games in 1970 and 32 in 1971. They inflate the competition header's club count (67 rather than 58) and give the clubs timeline nine one-season rows that were never NASL members. Same shape as the postseason item above — the games need their own competition or a round that marks them.
- [ ] Move the league -> playoffs-competition mapping (`PLAYOFF_CHAMPIONSHIPS` in `competitions/models.py`) out of s2 code and into data (metadata), the way competition definitions and aliases already work. It's data, not logic, and it'll only grow as more leagues (WUSA, WPS, NWSL, ...) get their postseasons split out. Two readers now: `Season.champion()` and `most_titled()` in `competitions/views.py`.

## Bios

Things that aren't people are filed as bios, and the news pages now surface them
as the most-mentioned "people" (`Red card:` on 634 stories). Four classes, each
minted by a different loader; fix each at its source rather than filtering here.

- [ ] Transactions: `load_transactions()` (`build/load.py`) calls `Bio.objects.find`
  on every `person` field, so draft picks, allocation money and cash become bios —
  `#14 2014 MLS SuperDraft pick`, `conditional 2013 draft pick`, `allocation
  ranking`, `cash`, ~170 in all, each holding exactly one transaction. Skip the
  bio when the text is a pick, allocation or cash; the transaction row can keep
  the text.
- [ ] Team awards: ten team names hold awards as bios — `North Carolina Courage`
  (3), `Portland Thorns`, `Seattle Reign`, `Richmond Kickers` (2 each), `Minnesota
  Thunder`, `Orlando Pride`, `Kansas City Current`, `Western New York Flash`,
  `Central Coast Roadrunners`, `Harrisburg City Islanders`. The awards loader needs
  to tell a team award from a player award and file it against the team.
- [ ] Lineup labels: `Red card:` (76 game stat lines), `Red cards:` (8), `ref:` and
  `free kick` (3) are trailing label lines read as players, nearly all in the USL
  First Division 1998–2002 lineup files (`parse/`), `free kick` in three scattered
  Open Cup and ASL games.
- [ ] Malformed names, ~300, mostly real people badly transcribed and holding real
  stats: leading colons (`: Ashlyn Harris`), parentheticals (`(Ray or Stan?)
  Morrison`, `(Dennis Chin 46 Alex Shinsky`), quoted nicknames (`"Flash" Gordon`,
  `"deactivated"Colmán`), digits. Source-file fixes, one at a time.
- [ ] Put a "Not people" section on `/bios/qa/` running these checks on every build
  (characters no name has, names matching a team, lowercase names, bios referenced
  only by a transaction), so the classes above stay at zero once fixed.
- [ ] 5,353 bios appear in nothing at all — no stats, games, lineups, awards, picks,
  coaching, positions, refereeing or transactions — about half with a birthdate, so
  real people from a bios source with thin holdings. Not wrong, but empty pages;
  decide whether the directory should show them, and mark on the page that the
  record holds nothing for them yet.
- [ ] The season goal chart groups by season *name* (`goal_seasons_by_tier`, `bios/views.py`), so a career mixing split-year club seasons with calendar-year caps splits across columns — `2013-2014`, `2013` and `2014` each get their own. Wondolowski's two CONCACAF Champions League seasons sit as 1- and 2-goal columns between the calendar years. Folding split-year seasons into their start year would misrepresent European careers, so this needs a decision about what a column means before it can be fixed.

## News

- [ ] Connect news to the rest of the record. People are done: `load_news()`
  matches each story's title, summary and archived text against every multi-word
  name in `Bio` and links it (`FeedItem.people`), so a story about Landon Donovan
  shows on his page. Teams, competitions and seasons are still unlinked; a 2010 du
  Nord roundup should show on the 2010 season page. Team names need aliasing the
  way the build already does it, and a season is a competition name plus a year.

## Deferred

- Competition headquarters, commissioner, and founding/folding dates on the competition header. `Competition` has no such fields and `organizations.Organization` is commented out, so this is a migration plus sourcing across ~229 competitions; the recorded season span is coverage, not a founding date. The header ships with recorded facts only.
- The error digest and the contact form both need `EMAIL_HOST_PASSWORD` (a Gmail app password for chris@soccerstats.us) in bert's `.env`. Until then the digest prints to its own journal and `/contact/` 500s with `SMTPSenderRefused`.
