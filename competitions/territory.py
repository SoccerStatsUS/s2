"""
The closest-club map: every county-grain unit of a league's country colored by
the club nearest its centre, for one season of a competition.

The units are places/counties.json, built by tools/county_map.py: US counties,
Canadian census divisions and Europe's NUTS 3 regions, each tagged with a
country code. A club is placed at its home city's coordinates (places.City
lat/lon, from metadata/data/places/cities). The units in play are those of
the countries the season's clubs are in -- MLS competes for the US and Canada,
the CPL for Canada alone, the Premier League for England -- and each goes to
the club with the shortest great-circle distance from its centroid. Clubs that
share a city are one territory, drawn in stripes of their colors, since the
point they share cannot be split by distance.

The frame follows the clubs: their bounding box, padded, widened to take in
whole units at the edge, drawn in an Albers equal-area conic centred on it.
The ASL is a map of the Northeast; MLS is a map of the continent. Units of
countries not in play that fall inside the frame are drawn as neutral ground,
so the coast and the border still read. Alaska and Hawaii get insets when the
US is in play and the frame leaves them out; the three Canadian territories
are counted but never drawn.

The page is heavy for this site -- thousands of outlines -- so each territory
is a single path of many subpaths rather than a path per unit.
"""

import json
import math
import os
from collections import defaultdict

from competitions.templatetags.charts import thin

ATLAS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "places", "counties.json")

WIDTH = 960

# A tall frame -- England, Italy -- fits to this height instead and comes
# out narrower than the column.
MAX_HEIGHT = 720

# The frame around the clubs: this share of the larger side of their bounding
# box on every edge, and never less than the floor in degrees, so two clubs in
# one city still get a map.
PADDING = 0.15
PADDING_FLOOR = 1.5

# A unit at the frame's edge pulls the frame out to its own extent, unless it
# is bigger than this many degrees across -- Nord-du-Quebec would otherwise
# stretch every map that reaches Montreal.
EDGE_UNIT_LIMIT = 6.0

# Units of the US and Canada centred north of this -- Yukon, the Northwest
# Territories and Nunavut -- are never drawn. tools/county_map.py thins them
# on the same line.
NORTH = 60.0

# Inset widths in pixels, and their padding from the frame's bottom-left.
ALASKA_WIDTH = 230
HAWAII_WIDTH = 110
INSET_GAP = 12

EARTH_RADIUS_KM = 6371.0

# How the database names a country, and the code the atlas files it under.
# The four home nations are their own countries here, as in football.
COUNTRY_CODES = {
    'United States': 'US', 'Canada': 'CA', 'Mexico': 'MX',
    'England': 'ENG', 'Wales': 'WLS', 'Scotland': 'SCT', 'Northern Ireland': 'NIR',
    'Albania': 'AL', 'Austria': 'AT', 'Belgium': 'BE', 'Bulgaria': 'BG',
    'Switzerland': 'CH', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Czechia': 'CZ',
    'Germany': 'DE', 'Denmark': 'DK', 'Estonia': 'EE', 'Greece': 'EL', 'Spain': 'ES',
    'Finland': 'FI', 'France': 'FR', 'Croatia': 'HR', 'Hungary': 'HU', 'Ireland': 'IE',
    'Iceland': 'IS', 'Italy': 'IT', 'Liechtenstein': 'LI', 'Lithuania': 'LT',
    'Luxembourg': 'LU', 'Latvia': 'LV', 'Montenegro': 'ME', 'North Macedonia': 'MK',
    'Macedonia': 'MK', 'Malta': 'MT', 'Netherlands': 'NL', 'Norway': 'NO', 'Poland': 'PL',
    'Portugal': 'PT', 'Romania': 'RO', 'Serbia': 'RS', 'Sweden': 'SE', 'Slovenia': 'SI',
    'Slovakia': 'SK', 'Turkey': 'TR',
    'Guatemala': 'GT', 'Belize': 'BZ', 'Honduras': 'HN', 'El Salvador': 'SV',
    'Nicaragua': 'NI', 'Costa Rica': 'CR', 'Panama': 'PA',
}

COUNTRY_NAMES = {code: name for name, code in COUNTRY_CODES.items()}
COUNTRY_NAMES.update({'CZ': 'Czech Republic', 'MK': 'North Macedonia'})

# What the units are called, for the caption and the table.
UNIT_NOUNS = {'US': 'counties', 'CA': 'census divisions', 'MX': 'municipios',
              'GT': 'municipios', 'HN': 'municipios', 'SV': 'municipios', 'NI': 'municipios',
              'CR': 'cantones', 'PA': 'distritos', 'BZ': 'constituencies'}
DEFAULT_NOUN = 'NUTS 3 regions'

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
    # 1970-71 -- Coventry, Hertha, Bangu and the rest -- are left to the
    # fallback on purpose: they hold no ground here, and the ROADMAP has them
    # leaving the league table altogether. Portland, San Jose, Seattle and
    # Vancouver are the same team rows as the MLS clubs and keep their colors.
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
    'new-england-tea-men': '#ff7f50',
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
    'toronto-falcons': '#d63384',
    'tulsa-roughnecks': '#00bcd4',
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

# Clubs with no color of their own cycle through these, in name order, so a
# league nobody has researched yet still draws legibly. Muted on purpose:
# the caption says they are not club colors.
FALLBACK = ('#8c9bab', '#b08968', '#7fa27a', '#a98ab0', '#c2a26a',
            '#79a3b5', '#b58a8a', '#8fa66f')

_atlas = None


def atlas():
    global _atlas
    if _atlas is None:
        with open(ATLAS_PATH, encoding="utf-8") as f:
            _atlas = json.load(f)["units"]
    return _atlas


def country_code(name):
    return COUNTRY_CODES.get(name or '')


def unit_noun(code):
    return UNIT_NOUNS.get(code, DEFAULT_NOUN)


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
    patterns are stable between renders. Clubs without a color of their own
    take the fallback set in turn, and the territory says so.
    """
    by_point = defaultdict(list)
    for club in clubs:
        by_point[(round(club["lat"], 3), round(club["lon"], 3))].append(club)

    out = []
    for (lat, lon), members in by_point.items():
        members.sort(key=lambda c: c["name"])
        out.append({
            "clubs": members,
            "name": " / ".join(c["name"] for c in members),
            "lat": lat, "lon": lon,
        })

    out.sort(key=lambda t: t["name"])
    generic = 0
    for i, t in enumerate(out):
        t["index"] = i
        colors = []
        for c in t["clubs"]:
            color = COLORS.get(c["slug"])
            if color is None:
                color = FALLBACK[generic % len(FALLBACK)]
                generic += 1
                t["generic"] = True
            colors.append(color)
        t["colors"] = colors
        t["color"] = colors[0]
    return out


def in_play(units, countries):
    """The units of the given country codes."""
    return {uid: u for uid, u in units.items() if u["country"] in countries}


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


ALASKA = albers(-154, 50, 55, 65)
HAWAII = albers(-157, 13, 8, 18)


class Frame:
    """
    The window the map shows, in degrees: the clubs' bounding box padded, then
    widened to whole units at the edge. Carries the projection for it.
    """

    def __init__(self, clubs, units):
        lons = [c["lon"] for c in clubs]
        lats = [c["lat"] for c in clubs]
        span = max(max(lons) - min(lons), max(lats) - min(lats))
        pad = max(PADDING * span, PADDING_FLOOR)
        self.west, self.east = min(lons) - pad, max(lons) + pad
        self.south, self.north = min(lats) - pad, max(lats) + pad

        # One pass only: widening lets in new centroids, and going round again
        # creeps along the coast until a Northeast map is half the continent.
        # Units let in by the widening are clipped at the edge, which reads
        # fine.
        box = (self.west, self.east, self.south, self.north)
        for unit in units.values():
            if box[0] <= unit["lon"] <= box[1] and box[2] <= unit["lat"] <= box[3]:
                x0, y0, x1, y1 = unit_bounds(unit)
                if max(x1 - x0, y1 - y0) <= EDGE_UNIT_LIMIT:
                    self.west, self.east = min(self.west, x0), max(self.east, x1)
                    self.south, self.north = min(self.south, y0), max(self.north, y1)

        self.south, self.north = max(self.south, -89.0), min(self.north, 89.0)
        sixth = (self.north - self.south) / 6
        self.project = albers((self.west + self.east) / 2, (self.south + self.north) / 2,
                              self.south + sixth, self.north - sixth)

    def holds(self, lon, lat):
        return self.west <= lon <= self.east and self.south <= lat <= self.north

    def touches(self, unit):
        x0, y0, x1, y1 = unit_bounds(unit)
        return x1 >= self.west and x0 <= self.east and y1 >= self.south and y0 <= self.north

    def outline(self, step=0.5):
        """The frame's edges as a ring of points, for fitting."""
        points = []
        lon, lat = self.west, self.south
        while lon < self.east:
            points.append((lon, self.south))
            lon += step
        while lat < self.north:
            points.append((self.east, lat))
            lat += step
        while lon > self.west:
            points.append((lon, self.north))
            lon -= step
        while lat > self.south:
            points.append((self.west, lat))
            lat -= step
        return points


def unit_bounds(unit):
    if "bounds" not in unit:
        xs = [p[0] for ring in unit["rings"] for p in ring]
        ys = [p[1] for ring in unit["rings"] for p in ring]
        unit["bounds"] = (min(xs), min(ys), max(xs), max(ys))
    return unit["bounds"]


def far_north(unit):
    return unit["country"] in ("US", "CA") and unit["lat"] > NORTH


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

    def inside(self, x, y):
        return self.dx <= x <= self.dx + self.width and self.dy <= y <= self.dy + self.height


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
LABEL_HEIGHT = 10
LABEL_GLYPH = 4.3


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
    label per territory, stripe patterns for shared cities, neutral ground,
    and the table rows. Clubs are dicts with name, slug, lat, lon and country
    (the atlas code); the caller has already set aside any without
    coordinates. Clubs whose country the atlas does not hold still get a
    territory -- but there is nothing for them to claim, so they are reported
    rather than drawn.
    """
    all_units = atlas()
    terrs = territories(clubs)
    if not terrs:
        return None

    # A club whose city has no country on record -- Washington D.C. is one --
    # is in whatever country the nearest unit is.
    for c in clubs:
        if c.get("country") is None:
            nearest = min(all_units.values(),
                          key=lambda u: distance_km(c["lat"], c["lon"], u["lat"], u["lon"]))
            c["country"] = nearest["country"]

    # Countries in play, the one with the most clubs first: that order runs
    # the caption and the table columns.
    tally = defaultdict(int)
    for c in clubs:
        tally[c["country"]] += 1
    countries = sorted(tally, key=lambda code: (-tally[code], code))
    units = in_play(all_units, countries)
    if not units:
        return None

    assigned = assign(units, terrs)
    frame = Frame(clubs, units)

    # Where each unit is drawn: the frame, an inset, or nowhere. Alaska and
    # Hawaii are inset only on a map of the country -- one that frames at
    # least half of the counties -- not on a map of the Northeast.
    us_units = [u for u in units.values() if u["country"] == "US"]
    national = us_units and (
        sum(frame.holds(u["lon"], u["lat"]) for u in us_units) >= len(us_units) / 2)
    where = {}
    for uid, unit in units.items():
        if far_north(unit):
            where[uid] = None
        elif frame.touches(unit):
            # Anything reaching into the frame is drawn and clipped at the
            # edge, so the frame fills to its corners.
            where[uid] = "main"
        elif national and unit["country"] == "US" and unit["state"] == "AK":
            where[uid] = "alaska"
        elif national and unit["country"] == "US" and unit["state"] == "HI":
            where[uid] = "hawaii"
        else:
            where[uid] = None

    ground_ids = [uid for uid, unit in all_units.items()
                  if unit["country"] not in countries and not far_north(unit)
                  and frame.touches(unit)]

    # Fit the pixel box to the frame itself, not to the units in it: ground
    # at the edge would otherwise drag the box out to its own extent. The
    # conic bends the frame's edges, so they are walked rather than cornered;
    # whatever falls outside is clipped by the SVG.
    main = Fit(frame.project, [frame.outline()], WIDTH, MAX_HEIGHT)
    width, height = main.width, main.height
    fits = {"main": main}

    inset_ids = defaultdict(list)
    for uid, w in where.items():
        if w in ("alaska", "hawaii"):
            inset_ids[w].append(uid)
    # Insets sit in the frame's bottom-left corner, side by side, where a
    # North American frame is empty Pacific.
    x = INSET_GAP
    for name, project, inset_width in (("alaska", ALASKA, ALASKA_WIDTH),
                                       ("hawaii", HAWAII, HAWAII_WIDTH)):
        if inset_ids[name]:
            fit = Fit(project, [r for uid in inset_ids[name] for r in units[uid]["rings"]],
                      inset_width)
            fit.dx, fit.dy = x, height - fit.height - INSET_GAP
            fits[name] = fit
            x += fit.width + INSET_GAP

    paths = defaultdict(list)
    weight = defaultdict(float)
    moment = defaultdict(lambda: [0.0, 0.0])
    counts = defaultdict(lambda: defaultdict(int))
    undrawn = 0
    for uid, unit in units.items():
        t = assigned[uid]
        counts[t][unit["country"]] += 1
        w = where[uid]
        if not w:
            undrawn += 1
            continue
        fit = fits[w]
        for ring in unit["rings"]:
            points = fit.ring(ring)
            d = path(points)
            if d:
                paths[t].append(d)
            if w == "main":
                area, (cx, cy) = area_and_centroid(points)
                area = abs(area)
                weight[t] += area
                moment[t][0] += cx * area
                moment[t][1] += cy * area

    ground = []
    for uid in ground_ids:
        for ring in all_units[uid]["rings"]:
            d = path(main.ring(ring))
            if d:
                ground.append(d)

    marks = []
    for t in terrs:
        i = t["index"]
        by_country = {code: counts[i][code] for code in countries}
        total = sum(by_country.values())
        mark = {
            "d": " ".join(paths[i]),
            "fill": ("url(#stripe-%d)" % i) if len(t["colors"]) > 1 else t["color"],
            "colors": t["colors"],
            "generic": t.get("generic", False),
            "index": i,
            "name": t["name"],
            "clubs": t["clubs"],
            "by_country": [by_country[code] for code in countries],
            "total": total,
            "share": 100.0 * total / len(units),
        }
        if weight[i]:
            mark["label"] = {"x": round(moment[i][0] / weight[i]),
                             "y": round(moment[i][1] / weight[i])}
        else:
            # A territory that only holds insets or the far north is labelled
            # at its own city if that is in the frame.
            x, y = main.point(t["lon"], t["lat"])
            if main.inside(x, y):
                mark["label"] = {"x": round(x), "y": round(y)}
        marks.append(mark)

    marks.sort(key=lambda m: -m["total"])
    place_labels(marks, width)

    # Every city as a dot, so the reader can see the point each territory is
    # measured from.
    cities = []
    for t in terrs:
        x, y = main.point(t["lon"], t["lat"])
        if main.inside(x, y):
            cities.append({"cx": round(x), "cy": round(y), "name": t["name"]})

    return {
        "svg": {"width": round(width), "height": round(height)},
        "marks": marks,
        "stripes": [m for m in marks if len(m["colors"]) > 1],
        "cities": cities,
        "ground": " ".join(ground),
        "countries": [{"code": code, "name": COUNTRY_NAMES.get(code, code),
                       "noun": unit_noun(code)} for code in countries],
        # England and Wales share a noun; the caption says it once.
        "nouns": sorted({unit_noun(code) for code in countries}),
        "units": len(units),
        "undrawn": undrawn,
        "insets": sorted(name for name in fits if name != "main"),
        "generic": any(m["generic"] for m in marks),
        "unmapped": [t["name"] for t in terrs
                     if all(c["country"] not in countries for c in t["clubs"])],
    }
