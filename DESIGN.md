# DESIGN.md

Design rules for SoccerStats.us. 

These are standing constraints, not a task list. Bugs and one-time fixes live in issues.
If a rule below blocks something that clearly needs doing, say so rather than working
around it silently — the rule may be wrong.

---

## 0. What this site is

A reference work: American soccer data, 1866 to present, mostly sourced. 
The audience is people who look up the 1924 Fall River roster for pleasure.
They want density, accuracy, and honesty about gaps.

Two consequences that decide most design questions:

- **The data is the interface.** Tables are the primary content, not a supporting element.
  When density and decoration conflict, density wins.
- **Provenance is the product.** Anything that makes the site look careless about accuracy
  costs more than it would on an ordinary site. An unlabeled column or a blank cell reads
  as sloppiness even when the underlying data is sound.


## 1. Tokens

The palette lives in `static/css/style.css` under `:root`, annotated there. That file is
the source of truth; a second copy in this document would only drift out of sync with it.

Add nothing to the palette without a stated reason. A new color is a claim that a new
kind of meaning exists on the page.

---

## 2. Color discipline

Green is a scarce semantic resource. It is not the "link color."

**Do**
- Use `--accent` for: the wordmark, section headings, and prose links (links surrounded
  by non-link text).
- Let table cells inherit `--ink`. The table is navigable by contract; individual cells
  do not need to advertise it.
- Reveal `--accent` inside tables on `:hover` and `:focus-visible` only.

**Don't**
- Color every linked cell in a data table. When every cell is green, the accent carries
  no information and the grid becomes a wall of color.
- Use color as the only carrier of meaning anywhere. It must always be redundant with
  weight, position, or a glyph.

Reserve remaining accent capacity for data semantics (result, provenance, marked absence),
not for chrome.

---

## 3. Tables

The house style is agate: dense, ruled, quiet. Newspaper box-score *engineering*, not
newspaper *costume*. No sepia, no faux-aged paper, no blackletter.

**Required on every table**
- A `<caption>` or an `<h2>` immediately above it, naming what the table is.
- `<thead>` with `<th scope="col">`. Never let the first data row stand in as a header.
- A legend for any column whose meaning is not obvious from its label — including every
  parenthetical or italic secondary figure. If you add a derived column, you add its
  definition in the same commit.

**Style**
- Hairline rules between logical groups. No boxes, no full grid.
- No zebra striping. Striping compensates for ragged row heights; fix the raggedness instead.
- Row hover highlight for tracking across wide tables.
- Set a minimum row height. Long names truncate with ellipsis and expose the full value
  on hover/tap rather than wrapping to three lines.
- Omit columns that are empty for every row in the current view.

---

## 4. Narrow screens

One breakpoint, at 760px. Below it the multi-column layouts collapse to a single column
and wide tables scroll horizontally inside themselves (`display: block; overflow-x: auto`).

Tables do not restack as cards, and columns are not dropped to make them fit. A standings
row read across is the unit of meaning; breaking it into stacked label/value pairs destroys
the comparison the table exists to support. Horizontal scroll is the deliberate trade —
the reader gives up seeing every column at once and keeps the ability to compare rows.

If a table is genuinely unusable on a phone, the fix is fewer columns in that view (§3's
"omit columns that are empty for every row"), not a different shape.

---

## 5. Numerals

Numbers are the product; treat them as typography.

- `font-variant-numeric: tabular-nums` on every table.
- Right-align or decimal-align numeric columns. Never center them.
- Counts render as integers. `408.0` games is a formatting bug, not a value.
- Fractional values that are real (half-games, averages) keep a consistent decimal
  precision within a column.
- Wrap dates in `<time datetime="YYYY-MM-DD">`. One human-readable date format sitewide;
  do not let page titles use a different one from body copy.

---

## 6. Type

- **Serif for voice, sans for the record.** Prose gets the serif; tables, scores, and
  column headers get the neutral face. A competition page rendering entirely in sans
  means no one has written an introduction for it yet.
- Set an explicit scale. The wordmark sits at the top; section headings drop at least two
  steps below it. A heading must never compete with the wordmark for first read.
- Cap prose at 65–72ch. Tables take full width; prose does not.
- Two density registers: prose pages are loose, data pages are tight. Do not inherit one
  line-height across both.

---

## 7. Spacing

One base unit; every vertical gap is a multiple of it. Irregular spacing is the most
common way a page comes to look unmaintained.

---

## 8. Links and focus

- Prose links carry a persistent underline (`text-underline-offset: 0.2em`), not color alone.
- Table cells: no underline, no color, hover only (see §2).
- Visible `:focus-visible` ring — 2px `--accent` with offset. Never `outline: none`.
- Tap targets are 44px minimum. Pad the box; don't rely on the glyph.

---

## 9. Absence and uncertainty

The database is historical and incomplete. That is a feature to be displayed, not a flaw
to be hidden. **A blank cell reads as a bug; a marked gap reads as rigor.**

Distinguish these three cases visually, and never render any of them as an empty string:

| case | meaning | render |
|---|---|---|
| no record | the figure was never recorded or is lost | `—` with a title of "no record found" |
| none | the value is genuinely zero or nothing | `0` or `—` per column convention |
| not entered | exists in a source, not yet transcribed | distinct marker, links to how to contribute |

Never emit an empty `<a href="">`. If a value is missing, render the marker, not a link
to nothing.

Where coverage stops, say so in place. Do not let a page imply currency it doesn't have.

---

## 10. Copy

- Sentence case. Plain verbs. No filler.
- Name things as a reader recognizes them, never as the schema stores them.
- Every competition and major team page earns one to three sentences of context. The
  register is set by the existing homepage lines — *"baseball owners' six-week experiment"*,
  *"the steel company's team, American soccer's first dynasty."* Concrete, dry, specific.
  This voice is the reason to read this site instead of Wikipedia; it should not stop at
  the homepage.
- Empty states are invitations, not apologies. A player with no game log says what is
  missing and how to help, not "no data."

---

## 11. Page identity

Every page carries exactly one `<h1>`, naming the thing the page is about — the player,
the competition, the season, the date. The wordmark is not the h1; it is navigation that
happens to sit at the top of every page.

Every page sets a `{% block title %}`, rendering as `<page> | SoccerStats.us`, and no two
pages share one. Falling through to the default title is a bug: it means the template
never declared what it is.

Headings below the h1 name the tables under them (§3). Never skip a heading level to get
a particular size — that is what CSS is for.

---

## 12. Do not add

- Club crests or player photographs. Coverage would be wildly uneven across eras, which
  visually amplifies exactly the gaps the site is trying to report honestly. Type, rule,
  and space carry the identity.
- Era-specific pastiche (1920s newsprint, 1970s NASL, 1990s MLS). The range is 150 years;
  styling to one era claims it is the real subject.
- Decorative iconography, gradients, drop shadows, rounded cards.
- Any dependency that blocks first paint of the tables.
