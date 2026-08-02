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

```css
--ink:         #1a1a1a;   /* body text; page ground is plain #fff */
--ink-soft:    #55606a;   /* secondary text, must hit 4.5:1 on white */
--accent:      #0b6e4f;   /* the green */
--accent-dark: #085239;   /* accent on hover/darker contexts */
--hairline:    #e5e7e9;   /* hairlines */
--fill:        #f6f7f8;   /* subtle panel/row ground */
--fill-hover:  #eef4f1;   /* row hover highlight */
--win:         #d9f0e1;   /* result semantics: win */
--loss:        #f8dcd9;   /* result semantics: loss */
--tie:         #faf0cf;   /* result semantics: tie */
```

Add nothing to this palette without a stated reason. A new color is a claim that a new
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

## 4. Numerals

Numbers are the product; treat them as typography.

- `font-variant-numeric: tabular-nums` on every table.
- Right-align or decimal-align numeric columns. Never center them.
- Counts render as integers. `408.0` games is a formatting bug, not a value.
- Fractional values that are real (half-games, averages) keep a consistent decimal
  precision within a column.
- Wrap dates in `<time datetime="YYYY-MM-DD">`. One human-readable date format sitewide;
  do not let page titles use a different one from body copy.

---

## 5. Type

- **Serif for voice, sans for the record.** Prose gets the serif; tables, scores, and
  column headers get the neutral face. This is functional as well as aesthetic: if a
  competition page renders entirely in sans, no one has written an introduction for it yet.
- Set an explicit scale (1.25 works). The wordmark sits at the top; section headings drop
  at least two steps below it. A heading must never compete with the wordmark for first read.
- Cap prose at 65–72ch. Tables take full width; prose does not.
- Two density registers: prose pages are loose, data pages are tight. Do not inherit one
  line-height across both.

---

## 6. Spacing

One base unit; every vertical gap is a multiple of it. Do not introduce ad-hoc margins.
Nothing else improves perceived craft this cheaply, and irregular spacing is the most
common way a page comes to look unmaintained.

---

## 7. Links, focus, and states

- Prose links carry a persistent underline (`text-underline-offset: 0.2em`), not color alone.
- Table cells: no underline, no color, hover only (see §2).
- Visible `:focus-visible` ring — 2px `--accent` with offset. Never `outline: none`.
- Tap targets are 44px minimum. Pad the box; don't rely on the glyph.
- Every interactive element needs empty, loading, and error states designed, not defaulted.

---

## 8. Absence and uncertainty

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

## 9. Copy

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


## 11. Do not add

- Club crests or player photographs. Coverage would be wildly uneven across eras, which
  visually amplifies exactly the gaps the site is trying to report honestly. Type, rule,
  and space carry the identity.
- Era-specific pastiche (1920s newsprint, 1970s NASL, 1990s MLS). The range is 150 years;
  styling to one era claims it is the real subject.
- Decorative iconography, gradients, drop shadows, rounded cards.
- Any dependency that blocks first paint of the tables.