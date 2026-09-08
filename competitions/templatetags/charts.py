"""
Inline-SVG charts, one series in the site's accent -- except the stacked goal
chart, which needs a categorical palette and carries its own in the stylesheet.
The Python here does the geometry; the templates under templatetags/charts/
emit the markup. Every chart is followed by a table carrying the same numbers,
so nothing is only readable from the picture. Marks follow the house rules:
thin, rounded at the data end, hairline solid gridlines, values labeled
sparingly, text in ink.
"""

import math

from django import template

register = template.Library()

WIDTH = 960


def comma(n):
    return f"{n:,.0f}"


def nice_step(maximum, target_ticks=5):
    """A clean tick step (1, 2, 2.5, 5 x 10^k) giving about target_ticks lines."""
    if maximum <= 0:
        return 1
    raw = maximum / target_ticks
    magnitude = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * magnitude >= raw:
            return m * magnitude
    return 10 * magnitude


def cap_path(x, y, w, h, r=4):
    """A column with a rounded top and a square base, as an SVG path."""
    if h <= r:
        return f"M{x:.1f},{y + h:.1f}v{-h:.1f}h{w:.1f}v{h:.1f}z"
    return (f"M{x:.1f},{y + h:.1f}V{y + r:.1f}Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f}"
            f"H{x + w - r:.1f}Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f}V{y + h:.1f}Z")


def label_step(names, slot):
    """
    Label every Nth column, spaced off the longest name rather than a fixed
    guess: season names run from "1969" to "1921-1922", and the wide ones
    overprint each other at a spacing the narrow ones are fine with.
    """
    widest = max(len(name) for name in names) * 7 + 10
    return max(1, math.ceil(widest / slot))


def rule_ground(median, average, partial=False):
    """
    What the median rule will be drawn on, which is what it has to contrast
    with: the surface where the median reaches or passes the average and the
    rule clears the mark, the hollow of an outlined mark, or a filled mark. A
    median equal to the average counts as clearing it, so the rule stays
    visible instead of vanishing into the cap.
    """
    if median >= average:
        return "on-surface"
    return "on-hollow" if partial else "on-fill"


def tip_path(x, y, w, h, r=4):
    """A horizontal bar with a rounded right end and a square left end."""
    if w <= r:
        return f"M{x:.1f},{y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}z"
    return (f"M{x:.1f},{y:.1f}H{x + w - r:.1f}Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f}"
            f"V{y + h - r:.1f}Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f}H{x:.1f}Z")


@register.inclusion_tag("templatetags/charts/columns.html")
def column_chart(rows, caption):
    """
    One column per row, in the order given, height = row['average'], with a
    rule across it at row['median'] so the gap between the two shows how far a
    few big crowds carried the average. Rows without an average keep their slot
    so the timeline stays continuous. Rows with row['partial'] draw outlined
    rather than filled -- unless every column is partial, when the outline
    distinguishes nothing and the chart fills instead. Each row carries name,
    url, average, median, known, games.
    """
    rows = list(rows)
    values = [r["average"] for r in rows if r.get("average")]
    if len(values) < 3:
        return {"svg": None}

    height, left, right, top, bottom = 300, 60, 20, 12, 40
    plot_w, plot_h = WIDTH - left - right, height - top - bottom
    # A median above its average puts its rule above the cap, so the scale has
    # to hold the medians too, not just the columns.
    ceiling = max(values + [r["median"] for r in rows if r.get("median")])
    step = nice_step(ceiling)
    y_max = step * math.ceil(ceiling / step)
    if y_max - ceiling < 0.04 * y_max:  # keep the tallest cap off the top gridline
        y_max += step
    scale = plot_h / y_max

    slot = plot_w / len(rows)
    bar_w = min(24, max(2, slot - 2))
    every = max(1, math.ceil(64 / slot))  # label spacing so 9-character names never touch

    plotted = [r for r in rows if r.get("average")]
    outline = not all(r.get("partial") for r in plotted)

    columns, labels = [], []
    last_labeled = -every
    for i, r in enumerate(rows):
        x = left + i * slot + (slot - bar_w) / 2
        # Label every Nth season, and the last one when it has room.
        if i % every == 0 or (i == len(rows) - 1 and i - last_labeled >= every):
            labels.append({"x": x + bar_w / 2, "text": r["name"]})
            last_labeled = i
        if not r.get("average"):
            continue
        h = r["average"] * scale
        median = r.get("median")
        partial = outline and r.get("partial", False)
        columns.append({
            "path": cap_path(x, top + plot_h - h, bar_w, h),
            "partial": partial,
            "median": {"x1": x, "x2": x + bar_w, "y": top + plot_h - median * scale,
                       "css": rule_ground(median, r["average"], partial)} if median else None,
            "url": r.get("url"),
            "title": "%s: %s average, %s median, over %s of %s games" % (
                r["name"], comma(r["average"]), comma(median or 0),
                comma(r["known"]), comma(r["games"])),
        })

    ticks = []
    v = 0
    while v <= y_max:
        ticks.append({"y": top + plot_h - v * scale, "text": comma(v)})
        v += step

    return {
        "svg": {"width": WIDTH, "height": height, "left": left,
                "right_edge": WIDTH - right, "base": top + plot_h,
                "label_y": top + plot_h + 18},
        "columns": columns, "labels": labels, "ticks": ticks,
        "caption": caption,
        "any_partial": any(c["partial"] for c in columns),
    }


# The stack, bottom to top, with the class the stylesheet colors it by. The
# order is also the legend order and the order the palette was validated in.
GOAL_TIERS = (
    ("us_d1", "us-d1", "US D1"),
    ("other_d1", "other-d1", "other D1"),
    ("non_d1", "non-d1", "non-D1 league"),
    ("cup", "cup", "cup"),
    ("international", "international", "international"),
)

GAP = 2  # surface gap between stacked segments


def block_path(x, y, w, h):
    """A square-cornered column segment, as an SVG path."""
    return f"M{x:.1f},{y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}z"


@register.inclusion_tag("templatetags/charts/player_goals.html")
def player_goals_chart(rows, caption):
    """
    One column per season, in the order given, split by competition tier.
    Each row carries name, goals, games and a tiers dict keyed by the tier
    names in GOAL_TIERS. Only tiers the player actually scored in appear in
    the legend.
    """
    rows = list(rows)
    values = [row["goals"] for row in rows if row["goals"] is not None]
    if len(rows) < 2 or not values or max(values) <= 0:
        return {"svg": None}

    legend_y, left, right, top, bottom = 12, 48, 20, 40, 40
    plot_h = 208
    height = top + plot_h + bottom
    plot_w = WIDTH - left - right
    step = nice_step(max(values))
    y_max = step * math.ceil(max(values) / step)
    if y_max - max(values) < 0.04 * y_max:
        y_max += step
    scale = plot_h / y_max
    slot = plot_w / len(rows)
    bar_w = min(36, max(8, slot * .65))
    every = max(1, math.ceil(56 / slot))
    base = top + plot_h

    columns = []
    for index, row in enumerate(rows):
        goals = row["goals"] or 0
        tiers = row.get("tiers") or {}
        x = left + index * slot + (slot - bar_w) / 2

        parts = [(css, label, tiers.get(tier) or 0) for tier, css, label in GOAL_TIERS]
        parts = [part for part in parts if part[2]]

        segments, y = [], base
        for position, (css, label, value) in enumerate(parts):
            y -= value * scale
            capped = position == len(parts) - 1  # only the top segment is rounded
            drawn = value * scale if capped else max(value * scale - GAP, 1.0)
            offset = 0 if capped else GAP
            segments.append({
                "css": css,
                "path": (cap_path if capped else block_path)(x, y + offset, bar_w, drawn),
                "title": "%s, %s: %s goal%s" % (
                    row["name"], label, comma(value), "" if value == 1 else "s"),
            })

        columns.append({
            "segments": segments,
            "x": x + bar_w / 2,
            "value_y": base - goals * scale - 5,
            "goals": goals,
            "name": row["name"] if index % every == 0 else "",
        })

    ticks = []
    value = 0
    while value <= y_max:
        ticks.append({"y": base - value * scale, "text": comma(value)})
        value += step

    keys, key_x = [], left
    for tier, css, label in GOAL_TIERS:
        if not any(row.get("tiers", {}).get(tier) for row in rows):
            continue
        keys.append({"css": css, "label": label, "x": key_x, "text_x": key_x + 14})
        key_x += 36 + len(label) * 6.2  # swatch, gap, text, then air before the next

    return {
        "svg": {
            "width": WIDTH,
            "height": height,
            "left": left,
            "right_edge": WIDTH - right,
            "base": base,
            "label_y": base + 18,
            "legend_y": legend_y,
            "swatch_y": legend_y - 9,
        },
        "columns": columns,
        "ticks": ticks,
        "keys": keys,
        "caption": caption,
    }


@register.inclusion_tag("templatetags/charts/counts.html")
def count_chart(rows, caption, noun):
    """
    One column per row, height = row['count']. A plain count of things, so no
    median rule; the axis carries the values and the hover title the exact
    figure, rather than a number stamped on every column.
    """
    rows = list(rows)
    values = [row["count"] for row in rows]
    if len(rows) < 3 or not any(values):
        return {"svg": None}

    height, left, right, top, bottom = 220, 40, 20, 20, 40
    plot_w, plot_h = WIDTH - left - right, height - top - bottom
    step = nice_step(max(values), target_ticks=4)
    y_max = step * math.ceil(max(values) / step)
    if y_max <= max(values):
        y_max += step
    scale = plot_h / y_max
    slot = plot_w / len(rows)
    bar_w = min(36, max(6, slot * .7))
    every = label_step([row["name"] for row in rows], slot)
    base = top + plot_h

    columns = []
    for index, row in enumerate(rows):
        x = left + index * slot + (slot - bar_w) / 2
        bar_h = row["count"] * scale
        columns.append({
            "path": cap_path(x, base - bar_h, bar_w, bar_h) if row["count"] else None,
            "x": x + bar_w / 2,
            "count": row["count"],
            "name": row["name"] if index % every == 0 else "",
            "title": "%s: %s %s" % (row["name"], comma(row["count"]), noun),
        })

    ticks = []
    value = 0
    while value <= y_max:
        ticks.append({"y": base - value * scale, "text": comma(value)})
        value += step

    return {
        "svg": {"width": WIDTH, "height": height, "left": left,
                "right_edge": WIDTH - right, "base": base, "label_y": base + 18},
        "columns": columns, "ticks": ticks, "caption": caption,
    }


@register.inclusion_tag("templatetags/charts/timeline.html")
def timeline_chart(timeline, caption, noun="clubs"):
    """
    A club per row, a season per column, a block where the two meet. Rows come
    in the order given; the blocks are drawn per season rather than as one span
    from first to last, so a club that left and came back shows the gap.
    """
    columns, rows = timeline.get("columns") or [], timeline.get("rows") or []
    if len(columns) < 2 or len(rows) < 2:
        return {"svg": None}

    row_h, block_h, left, right, top = 15, 9, 210, 20, 26
    plot_w = WIDTH - left - right
    slot = plot_w / len(columns)
    block_w = max(2, slot - GAP)
    every = label_step(columns, slot)

    # The rows run far past the labels at the top, so each labeled season also
    # gets a rule down the chart to track it by.
    marks, labels = [], []
    last_labeled = -every
    for index, name in enumerate(columns):
        # Label every Nth season, and the last one only when it has the room.
        if index % every == 0 or (index == len(columns) - 1 and index - last_labeled >= every):
            labels.append({"x": left + index * slot + slot / 2, "text": name})
            last_labeled = index

    for position, row in enumerate(rows):
        y = top + position * row_h
        span = "%s%s" % (row["first"], "" if row["last"] == row["first"] else "-%s" % row["last"])
        blocks = [{
            "x": left + index * slot + (slot - block_w) / 2,
            "y": y + (row_h - block_h) / 2,
            "width": block_w,
        } for index, name in enumerate(columns) if name in row["seasons"]]
        marks.append({
            "blocks": blocks,
            "label_y": y + row_h / 2 + 4,
            "name": row["name"],
            "url": row.get("url"),
            "title": "%s: %s season%s, %s" % (
                row["name"], comma(row["played"]), "" if row["played"] == 1 else "s", span),
        })

    height = top + len(rows) * row_h + 6
    for label in labels:
        label["grid_top"] = top - 6
        label["grid_bottom"] = height

    return {
        "svg": {"width": WIDTH, "height": height, "left": left, "label_x": left - 10,
                "block_h": block_h, "label_y": top - 12, "base": height},
        "marks": marks, "labels": labels, "caption": caption,
        "one": noun[:-1] if noun.endswith("s") else noun,
    }


@register.inclusion_tag("templatetags/charts/bars.html")
def bar_chart(rows, caption):
    """
    One horizontal bar per row, in the order given, length = row['average'],
    with a rule across it at row['median'] so the gap between the two shows how
    far a few big crowds carried the average. Each row carries name, url,
    average, median, games, total.
    """
    rows = list(rows)
    if len(rows) < 3:
        return {"svg": None}

    row_h, bar_h, left, right, top = 22, 14, 230, 70, 6
    plot_w = WIDTH - left - right
    # A median above its average puts its rule past the tip, so the scale has
    # to hold the medians too, not just the bars.
    y_max = max([r["average"] for r in rows] + [r["median"] for r in rows if r.get("median")])
    scale = plot_w / y_max if y_max else 0

    bars = []
    for i, r in enumerate(rows):
        y = top + i * row_h
        w = r["average"] * scale
        bar_y = y + (row_h - bar_h) / 2
        median = r.get("median")
        # A median above the average puts its rule past the bar's tip, so the
        # value sits clear of whichever of the two reaches furthest right.
        reach = max(w, median * scale if median else 0)
        bars.append({
            "path": tip_path(left, bar_y, w, bar_h),
            "median": {"x": left + median * scale, "y1": bar_y, "y2": bar_y + bar_h,
                       "css": rule_ground(median, r["average"])} if median else None,
            "label_y": y + row_h / 2 + 4,
            "value_x": left + reach + 6,
            "value": comma(r["average"]),
            "name": r["name"],
            "url": r.get("url"),
            "title": "%s: %s average, %s median, over %s home games, %s in all" % (
                r["name"], comma(r["average"]), comma(median or 0),
                comma(r["games"]), comma(r["total"])),
        })

    height = top + len(rows) * row_h + 6
    return {
        "svg": {"width": WIDTH, "height": height + 16, "left": left, "label_x": left - 10,
                "base": height},
        "bars": bars, "caption": caption,
    }
