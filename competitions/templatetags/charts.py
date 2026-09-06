"""
Inline-SVG charts for one series, in the site's accent. The Python here does
the geometry; the templates under templatetags/charts/ emit the markup. Every
chart is followed by a table carrying the same numbers, so nothing is only
readable from the picture. Marks follow the house rules: thin, rounded at the
data end, hairline solid gridlines, values labeled sparingly, text in ink.
"""

import math
import statistics

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


def tip_path(x, y, w, h, r=4):
    """A horizontal bar with a rounded right end and a square left end."""
    if w <= r:
        return f"M{x:.1f},{y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}z"
    return (f"M{x:.1f},{y:.1f}H{x + w - r:.1f}Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f}"
            f"V{y + h - r:.1f}Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f}H{x:.1f}Z")


@register.inclusion_tag("templatetags/charts/columns.html")
def column_chart(rows, caption):
    """
    One column per row, in the order given, height = row['average']. Rows
    without an average keep their slot so the timeline stays continuous. Rows
    with row['partial'] draw outlined rather than filled. Each row carries
    name, url, average, known, games. A labeled line marks the median of the
    plotted averages.
    """
    rows = list(rows)
    values = [r["average"] for r in rows if r.get("average")]
    if len(values) < 3:
        return {"svg": None}

    height, left, right, top, bottom = 300, 60, 96, 12, 40  # right margin holds the median label
    plot_w, plot_h = WIDTH - left - right, height - top - bottom
    step = nice_step(max(values))
    y_max = step * math.ceil(max(values) / step)
    if y_max - max(values) < 0.04 * y_max:  # keep the tallest cap off the top gridline
        y_max += step
    scale = plot_h / y_max

    slot = plot_w / len(rows)
    bar_w = min(24, max(2, slot - 2))
    every = max(1, math.ceil(64 / slot))  # label spacing so 9-character names never touch

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
        columns.append({
            "path": cap_path(x, top + plot_h - h, bar_w, h),
            "partial": r.get("partial", False),
            "url": r.get("url"),
            "title": "%s: %s average over %s of %s games" % (
                r["name"], comma(r["average"]), comma(r["known"]), comma(r["games"])),
        })

    ticks = []
    v = 0
    while v <= y_max:
        ticks.append({"y": top + plot_h - v * scale, "text": comma(v)})
        v += step

    median = statistics.median(values)
    return {
        "svg": {"width": WIDTH, "height": height, "left": left,
                "right_edge": WIDTH - right, "base": top + plot_h,
                "label_y": top + plot_h + 18},
        "columns": columns, "labels": labels, "ticks": ticks,
        "median": {"y": top + plot_h - median * scale, "text": "median %s" % comma(median)},
        "caption": caption,
        "any_partial": any(c["partial"] for c in columns),
    }


@register.inclusion_tag("templatetags/charts/bars.html")
def bar_chart(rows, caption):
    """
    One horizontal bar per row, in the order given, length = row['average'].
    Each row carries name, url, average, games, total. A labeled line marks the
    median of the plotted averages.
    """
    rows = list(rows)
    if len(rows) < 3:
        return {"svg": None}

    row_h, bar_h, left, right, top = 22, 14, 230, 70, 6
    plot_w = WIDTH - left - right
    y_max = max(r["average"] for r in rows)
    scale = plot_w / y_max if y_max else 0

    bars = []
    for i, r in enumerate(rows):
        y = top + i * row_h
        w = r["average"] * scale
        bars.append({
            "path": tip_path(left, y + (row_h - bar_h) / 2, w, bar_h),
            "label_y": y + row_h / 2 + 4,
            "value_x": left + w + 6,
            "value": comma(r["average"]),
            "name": r["name"],
            "url": r.get("url"),
            "title": "%s: %s average over %s home games, %s in all" % (
                r["name"], comma(r["average"]), comma(r["games"]), comma(r["total"])),
        })

    median = statistics.median(r["average"] for r in rows)
    height = top + len(rows) * row_h + 6
    return {
        "svg": {"width": WIDTH, "height": height + 16, "left": left, "label_x": left - 10,
                "base": height},
        "bars": bars, "caption": caption,
        "median": {"x": left + median * scale, "text": "median %s" % comma(median)},
    }
