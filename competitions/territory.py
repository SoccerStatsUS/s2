"""
The closest-club map: every US county and Canadian census division colored by
the club nearest its centre, for one season of a competition.

The units are places/counties.json, built by tools/county_map.py. A club is
placed at its home city's coordinates (places.City.lat/lon, from
metadata/data/places/cities), and a unit goes to the club with the shortest
great-circle distance from the unit's centroid. Clubs that share a city are one
territory -- Los Angeles has held three at once -- drawn in stripes of their
colors, since the point they share cannot be split by distance.

Everything is drawn in one Albers equal-area conic frame covering the lower 48
and the ten provinces, with Alaska and Hawaii inset below it. The three
territories north of 60 degrees are counted in the table but not drawn.

The page is heavy for this site -- about 3,400 outlines -- so each territory is
a single path of many subpaths rather than a path per unit.
"""

import json
import math
import os
from collections import defaultdict

from competitions.templatetags.charts import ring_bounds, thin

ATLAS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "places", "counties.json")

WIDTH = 960

# Units centred north of this are outside the frame: Yukon, the Northwest
# Territories and Nunavut. tools/county_map.py thins them on the same line.
NORTH = 60.0

# Inset widths in pixels, and their padding from the frame's bottom-left.
ALASKA_WIDTH = 230
HAWAII_WIDTH = 110
INSET_GAP = 12

EARTH_RADIUS_KM = 6371.0

# One color per club, keyed by team slug. These are data encodings on one
# page, never the site palette (DESIGN.md section 2): every territory also
# carries its name, and the table repeats the assignment. Picked from each
# club's own colors, then pushed apart wherever two territories that touch on
# some season's map came out alike -- Sporting Kansas City and Minnesota
# United were the same sky blue on the map this one follows.
COLORS = {
    'atlanta-united': '#b59a5b',
    'austin-fc': '#2d8a3f',
    'charlotte-fc': '#1a85c8',
    'chicago-fire': '#1b2a5e',
    'chivas-usa': '#e8442d',
    'colorado-rapids': '#74b3e3',
    'columbus-crew': '#f2c61b',
    'dc-united': '#2b2b2b',
    'fc-cincinnati': '#f36b21',
    'fc-dallas': '#d92038',
    'houston-dynamo': '#ee7a1a',
    'inter-miami': '#f18ab5',
    'la-galaxy': '#0d2b5c',
    'los-angeles-fc': '#c9a44a',
    'miami-fusion': '#e0a526',
    'minnesota-united-fc': '#6e7b86',
    'montreal-impact': '#2b5fc7',
    'nashville-sc': '#e9d44d',
    'new-england-revolution': '#1d3a6e',
    'new-york-city-fc': '#6cace4',
    'new-york-red-bulls': '#c8102e',
    'orlando-city-sc': '#5c2d91',
    'philadelphia-union': '#3b5f9b',
    'portland-timbers': '#1e5a34',
    'real-salt-lake': '#a3243b',
    'saint-louis-city-sc': '#7ec8ec',
    'san-diego-fc': '#00b2e3',
    'san-jose-earthquakes': '#0a5bbf',
    'seattle-sounders': '#5fb62c',
    'sporting-kansas-city': '#2a8ccc',
    'tampa-bay-mutiny': '#1f9e8a',
    'toronto-fc': '#7a1538',
    'vancouver-whitecaps': '#0b2d6b',

    # NASL, 1968-1984. Kit colors where they are on record (nasljerseys.com,
    # funwhileitlasted.net, sportslogos.net); the rest are chosen to stand
    # apart from the neighbors of their years. The touring guest clubs of
    # 1970-71 -- Coventry, Hertha, Bangu and the rest -- are left grey on
    # purpose: they hold no ground here, and the ROADMAP has them leaving the
    # league table altogether. Portland, San Jose, Seattle and Vancouver are
    # the same team rows as the MLS clubs and keep their colors above.
    'atlanta-chiefs': '#5e2b97',
    'baltimore-bays': '#f0b323',
    'baltimore-comets': '#7b3f9e',
    'boston-beacons': '#1f4e9a',
    'boston-minutemen': '#c41e3a',
    'calgary-boomers': '#8e2020',
    'california-surf': '#2e6fd8',
    'chicago-mustangs': '#0aa4d8',
    'chicago-sting': '#f5c400',
    'cleveland-stokers': '#d0202e',
    'colorado-caribous': '#7a4a1e',
    'connecticut-bicentennials': '#1d3f8b',
    'dallas-tornado': '#1e4b9c',
    'denver-dynamos': '#6a3d9a',
    'detroit-cougars': '#2a7f62',
    'detroit-express': '#2d9cdb',
    'edmonton-drillers': '#2a7de1',
    'fort-lauderdale-strikers': '#e3242b',
    'houston-hurricane': '#f4711f',
    'houston-stars': '#c93c20',
    'kansas-city-spurs': '#d4a017',
    'las-vegas-quicksilvers': '#c0c0c0',
    'los-angeles-aztecs': '#f9c623',
    'los-angeles-wolves': '#1a1a1a',
    'memphis-rogues': '#6fb3e0',
    'miami-toros': '#f7941d',
    'minnesota-kicks': '#f26522',
    'minnesota-strikers': '#e3242c',
    'montreal-manic': '#3b82d6',
    'montreal-olympique': '#7a1fa2',
    'new-england-tea-men': '#274b9f',
    'new-york-cosmos': '#0a7d3b',
    'new-york-generals': '#8a3ab9',
    'oakland-clippers': '#2e8b57',
    'oakland-stompers': '#a31f34',
    'philadelphia-atoms': '#f0e130',
    'philadelphia-fury': '#5dade2',
    'rochester-lancers': '#6b8e23',
    'san-antonio-thunder': '#d9a300',
    'san-diego-jaws': '#4a90d9',
    'san-diego-sockers': '#1d2951',
    'san-diego-toros': '#8c1d40',
    'st-louis-stars': '#1b7f3b',
    'tampa-bay-rowdies': '#7fd13b',
    'team-america': '#b31942',
    'team-hawaii': '#00a3e0',
    'toronto-blizzard': '#0b3d91',
    'toronto-falcons': '#f4a300',
    'tulsa-roughnecks': '#8e24aa',
    'vancouver-royals': '#2a52be',
    'washington-darts': '#e8a317',
    'washington-diplomats': '#c8202f',
    'washington-whips': '#2e9e6b',

    # Canadian Premier League, 2019-. Club colors as announced; Inter Toronto
    # is the York United row renamed, and takes its 2025 Lake Ontario blue.
    'atletico-ottawa': '#d41c2c',
    'cavalry-fc': '#1f6f3f',
    'fc-edmonton': '#143d7a',
    'forge-fc': '#f47a1f',
    'hfx-wanderers': '#3aa1d8',
    'inter-toronto-fc': '#1f5fbf',
    'pacific-fc': '#5a2d82',
    'valour-fc': '#7b1e3a',
    'vancouver-fc': '#d64541',
}

UNASSIGNED = '#9a9a9a'

_atlas = None


def atlas():
    global _atlas
    if _atlas is None:
        with open(ATLAS_PATH, encoding="utf-8") as f:
            _atlas = json.load(f)["units"]
    return _atlas


# ---- Assignment ---------------------------------------------------------

def distance_km(lat1, lon1, lat2, lon2):
    """Great-circle distance by the haversine formula."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def territories(clubs):
    """
    Group clubs by location. Each club is a dict with name, slug, lat and lon;
    each territory carries its clubs, its point, and a color -- one club's
    own, or a stripe of several. Ordered by name so the table and the stripe
    patterns are stable between renders.
    """
    by_point = defaultdict(list)
    for club in clubs:
        by_point[(round(club["lat"], 3), round(club["lon"], 3))].append(club)

    out = []
    for (lat, lon), members in by_point.items():
        members.sort(key=lambda c: c["name"])
        colors = [COLORS.get(c["slug"], UNASSIGNED) for c in members]
        out.append({
            "clubs": members,
            "name": " / ".join(c["name"] for c in members),
            "lat": lat, "lon": lon,
            "colors": colors,
            "color": colors[0],
        })

    out.sort(key=lambda t: t["name"])
    for i, t in enumerate(out):
        t["index"] = i
    return out


def assign(units, territories_):
    """Map each unit id to the index of the nearest territory."""
    points = [(t["lat"], t["lon"]) for t in territories_]
    assigned = {}
    for uid, unit in units.items():
        best, best_d = None, None
        for i, (lat, lon) in enumerate(points):
            d = distance_km(unit["lat"], unit["lon"], lat, lon)
            if best_d is None or d < best_d:
                best, best_d = i, d
        assigned[uid] = best
    return assigned


# ---- Projection ---------------------------------------------------------

def albers(lon0, lat0, lat1, lat2):
    """
    Albers equal-area conic on the sphere (Snyder, p. 100). Returns a function
    from (lon, lat) in degrees to (x, y) in earth radii, y upward.
    """
    p0, p1, p2 = math.radians(lat0), math.radians(lat1), math.radians(lat2)
    n = (math.sin(p1) + math.sin(p2)) / 2
    c = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = math.sqrt(c - 2 * n * math.sin(p0)) / n
    l0 = math.radians(lon0)

    def project(lon, lat):
        rho = math.sqrt(max(c - 2 * n * math.sin(math.radians(lat)), 0.0)) / n
        theta = n * (math.radians(lon) - l0)
        return rho * math.sin(theta), rho0 - rho * math.cos(theta)

    return project


MAIN = albers(-96, 40, 33, 55)
ALASKA = albers(-154, 50, 55, 65)
HAWAII = albers(-157, 13, 8, 18)


def frame_of(unit):
    """Which projection a unit belongs to, or None if it is not drawn."""
    if unit["state"] == "AK":
        return "alaska"
    if unit["state"] == "HI":
        return "hawaii"
    if unit["lat"] > NORTH:
        return None
    return "main"


class Fit:
    """Projected coordinates scaled and shifted into a pixel box."""

    def __init__(self, project, rings, width, height=None):
        self.project = project
        xs, ys = [], []
        for ring in rings:
            for lon, lat in ring:
                x, y = project(lon, lat)
                xs.append(x)
                ys.append(y)
        self.x0, self.x1 = min(xs), max(xs)
        self.y0, self.y1 = min(ys), max(ys)
        self.scale = width / (self.x1 - self.x0)
        if height is not None:
            self.scale = min(self.scale, height / (self.y1 - self.y0))
        self.width = (self.x1 - self.x0) * self.scale
        self.height = (self.y1 - self.y0) * self.scale
        self.dx = self.dy = 0.0

    def point(self, lon, lat):
        x, y = self.project(lon, lat)
        return ((x - self.x0) * self.scale + self.dx, (self.y1 - y) * self.scale + self.dy)

    def ring(self, ring):
        return [self.point(lon, lat) for lon, lat in ring]


def area_and_centroid(points):
    """Signed area and centroid of a projected ring, by the shoelace formula."""
    area = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(area) < 1e-9:
        return 0.0, (0.0, 0.0)
    return area / 2, (cx / (3 * area), cy / (3 * area))


def path(points):
    points = thin(points)
    if len(points) < 3:
        return ""
    return "M" + "L".join("%d,%d" % p for p in points) + "Z"


# Label metrics, in pixels: the em box the CSS gives the text, and an average
# glyph width for a sans-serif at that size, which is what the collision pass
# has to go on without a font in reach.
LABEL_HEIGHT = 14
LABEL_GLYPH = 6.4


def place_labels(marks, width):
    """
    Keep labels inside the frame and off each other. Bigger territories are
    placed first and stay put; a smaller one whose box lands on a placed label
    steps down a line at a time until it clears -- the New York clubs and the
    Florida ones sit a few pixels apart otherwise. Marks arrive sorted largest
    first.
    """
    placed = []
    for mark in marks:
        label = mark.get("label")
        if not label:
            continue

        half = len(mark["name"]) * LABEL_GLYPH / 2
        x = min(max(label["x"], half + 2), width - half - 2)
        y = label["y"]

        def clashes(y):
            return any(abs(x - px) < half + ph and abs(y - py) < LABEL_HEIGHT
                       for px, py, ph in placed)

        tries = 0
        while clashes(y) and tries < 8:
            y += LABEL_HEIGHT
            tries += 1

        label["x"], label["y"] = round(x), round(y)
        placed.append((x, y, half))


# ---- The map ------------------------------------------------------------

def season_map(clubs):
    """
    Everything the template needs for one season: the SVG frame, a path and a
    label per territory, stripe patterns for shared cities, and the table rows.
    Clubs are dicts with name, slug, lat and lon; the caller has already set
    aside any without coordinates.
    """
    units = atlas()
    terrs = territories(clubs)
    if not terrs:
        return None

    assigned = assign(units, terrs)

    by_frame = defaultdict(list)
    for uid, unit in units.items():
        frame = frame_of(unit)
        if frame:
            by_frame[frame].append(uid)

    main = Fit(MAIN, [r for uid in by_frame["main"] for r in units[uid]["rings"]], WIDTH)
    alaska = Fit(ALASKA, [r for uid in by_frame["alaska"] for r in units[uid]["rings"]], ALASKA_WIDTH)
    hawaii = Fit(HAWAII, [r for uid in by_frame["hawaii"] for r in units[uid]["rings"]], HAWAII_WIDTH)

    # Insets sit in the frame's bottom-left corner, side by side: the Pacific
    # off Baja California, which the projection leaves empty because Mexico
    # is not drawn. The frame keeps the main map's height.
    height = main.height
    alaska.dx, alaska.dy = INSET_GAP, height - alaska.height - INSET_GAP
    hawaii.dx, hawaii.dy = INSET_GAP * 2 + alaska.width, height - hawaii.height - INSET_GAP
    fits = {"main": main, "alaska": alaska, "hawaii": hawaii}

    paths = defaultdict(list)
    weight = defaultdict(float)
    moment = defaultdict(lambda: [0.0, 0.0])
    counts = defaultdict(lambda: defaultdict(int))
    for uid, unit in units.items():
        t = assigned[uid]
        counts[t][unit["country"]] += 1
        frame = frame_of(unit)
        if not frame:
            counts[t]["north"] += 1
            continue
        fit = fits[frame]
        for ring in unit["rings"]:
            points = fit.ring(ring)
            d = path(points)
            if d:
                paths[t].append(d)
            if frame == "main":
                area, (cx, cy) = area_and_centroid(points)
                area = abs(area)
                weight[t] += area
                moment[t][0] += cx * area
                moment[t][1] += cy * area

    marks = []
    for t in terrs:
        i = t["index"]
        mark = {
            "d": " ".join(paths[i]),
            "fill": ("url(#stripe-%d)" % i) if len(t["colors"]) > 1 else t["color"],
            "colors": t["colors"],
            "index": i,
            "name": t["name"],
            "clubs": t["clubs"],
            "us": counts[i]["US"],
            "ca": counts[i]["CA"],
            "north": counts[i]["north"],
        }
        mark["total"] = mark["us"] + mark["ca"]
        mark["share"] = 100.0 * mark["total"] / len(units)
        if weight[i]:
            mark["label"] = {"x": round(moment[i][0] / weight[i]),
                             "y": round(moment[i][1] / weight[i])}
        else:
            # A territory that only holds insets or the far north is labelled
            # at its own city if that is in the frame.
            x, y = main.point(t["lon"], t["lat"])
            if 0 <= x <= main.width and 0 <= y <= main.height:
                mark["label"] = {"x": round(x), "y": round(y)}
        marks.append(mark)

    marks.sort(key=lambda m: -m["total"])
    place_labels(marks, WIDTH)

    # Every city as a dot, so the reader can see the point each territory is
    # measured from.
    cities = []
    for t in terrs:
        x, y = main.point(t["lon"], t["lat"])
        if 0 <= x <= main.width and 0 <= y <= main.height:
            cities.append({"cx": round(x), "cy": round(y), "name": t["name"]})

    return {
        "svg": {"width": round(WIDTH), "height": round(height)},
        "marks": marks,
        "stripes": [m for m in marks if len(m["colors"]) > 1],
        "cities": cities,
        "units": len(units),
        "north": sum(counts[i]["north"] for i in counts),
    }
