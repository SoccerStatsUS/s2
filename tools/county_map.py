"""
Build places/counties.json, the US counties and Canadian census divisions the
closest-club territory map colors in.

Sources, both public domain:

  US Census Bureau, cartographic boundary file, counties, 2020, 1:20m.
  https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_20m.zip
  2020 rather than a later vintage: Connecticut replaced its counties with
  planning regions in 2022, and a map of counties should hold counties.

  Statistics Canada, 2021 census, census divisions, cartographic boundary.
  https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lcd_000b21a_e.zip
  The one Canadian unit that is roughly county-sized everywhere (a county in
  Ontario or Nova Scotia, an MRC in Quebec, a regional district in BC).
  Delivered in Statistics Canada's Lambert projection, so it is unprojected
  here; the .prj file carries the parameters below.

Both are shapefiles, which need a reader the site does not otherwise want:

    uv pip install -p .venv/bin/python pyshp
    .venv/bin/python tools/county_map.py cb_2020_us_county_20m.shp lcd_000b21a_e.shp
"""

import json
import math
import os
import sys

import shapefile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from world_map import extent, rings, simplify  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'places', 'counties.json')

# Degrees. About a pixel when the continent fills a thousand of them; finer
# than that is coastline the map cannot draw, and there are 3,400 units.
TOLERANCE = 0.012

# Units centred north of 60 degrees -- the three territories -- are outside
# the map's frame, so they are kept for the table and thinned to a sketch.
# Nunavut alone was a third of the file at the finer tolerance.
NORTH = 60.0
NORTH_TOLERANCE = 0.08

# Rings smaller than this in bounding-box degrees are dropped unless they are
# all a unit has. Islands cost points and color nothing anyone can see.
MIN_RING = 0.08

# Puerto Rico and the island territories: in the county file, in no MLS map.
SKIP_STATES = {'60', '66', '69', '72', '78'}

PROVINCES = {
    '10': 'NL', '11': 'PE', '12': 'NS', '13': 'NB', '24': 'QC', '35': 'ON',
    '46': 'MB', '47': 'SK', '48': 'AB', '59': 'BC', '60': 'YT', '61': 'NT',
    '62': 'NU',
}


# ---- Statistics Canada Lambert, inverse ---------------------------------
#
# Lambert conformal conic, two standard parallels, on GRS 1980. Snyder's
# formulas (Map Projections: A Working Manual, pp. 107-109).

A = 6378137.0
E = math.sqrt(2 / 298.257222101 - (1 / 298.257222101) ** 2)
LAT_0, LON_0 = math.radians(63.390675), math.radians(-91.86666666666666)
LAT_1, LAT_2 = math.radians(49.0), math.radians(77.0)
FALSE_EASTING, FALSE_NORTHING = 6200000.0, 3000000.0


def _m(lat):
    return math.cos(lat) / math.sqrt(1 - (E * math.sin(lat)) ** 2)


def _t(lat):
    s = E * math.sin(lat)
    return math.tan(math.pi / 4 - lat / 2) / ((1 - s) / (1 + s)) ** (E / 2)


N = (math.log(_m(LAT_1)) - math.log(_m(LAT_2))) / (math.log(_t(LAT_1)) - math.log(_t(LAT_2)))
F = _m(LAT_1) / (N * _t(LAT_1) ** N)
RHO_0 = A * F * _t(LAT_0) ** N


def unproject(x, y):
    """Statistics Canada Lambert metres to (lon, lat) in degrees."""
    x -= FALSE_EASTING
    y = RHO_0 - (y - FALSE_NORTHING)
    rho = math.copysign(math.hypot(x, y), N)
    theta = math.atan2(math.copysign(x, N), math.copysign(y, N))
    t = (rho / (A * F)) ** (1 / N)

    lat = math.pi / 2 - 2 * math.atan(t)
    for _ in range(6):
        s = E * math.sin(lat)
        lat = math.pi / 2 - 2 * math.atan(t * ((1 - s) / (1 + s)) ** (E / 2))

    return math.degrees(theta / N + LON_0), math.degrees(lat)


# ---- Geometry -----------------------------------------------------------

def centroid(ring):
    """Area-weighted centroid of a ring; its mean point if it has no area."""
    area = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(area) < 1e-12:
        return (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))
    return (cx / (3 * area), cy / (3 * area))


def unit(name, state, country, geometry, transform=None):
    outer = rings(geometry)
    if transform:
        outer = [[transform(x, y) for x, y in ring] for ring in outer]

    if state == 'AK':
        # The Aleutians cross the antimeridian; keep them on Alaska's side of
        # the frame instead of a ring that spans the globe.
        outer = [[(x - 360 if x > 0 else x, y) for x, y in ring] for ring in outer]

    outer.sort(key=extent, reverse=True)
    lon, lat = centroid(outer[0])

    tolerance = NORTH_TOLERANCE if lat > NORTH else TOLERANCE

    kept = []
    for i, ring in enumerate(outer):
        if i and extent(ring) < MIN_RING:
            continue
        simplified = [[round(x, 3), round(y, 3)] for x, y in simplify(ring, tolerance)]
        if len(simplified) >= 3:
            kept.append(simplified)

    if not kept:
        return None

    return {'name': name, 'state': state, 'country': country,
            'lon': round(lon, 4), 'lat': round(lat, 4), 'rings': kept}


def build(us_path, ca_path):
    units = {}

    for sr in shapefile.Reader(us_path).iterShapeRecords():
        props = sr.record.as_dict()
        if props['STATEFP'] in SKIP_STATES:
            continue
        u = unit(props['NAME'], props['STUSPS'], 'US', sr.shape.__geo_interface__)
        if u:
            units[props['GEOID']] = u

    for sr in shapefile.Reader(ca_path, encoding='latin-1').iterShapeRecords():
        props = sr.record.as_dict()
        u = unit(' '.join(props['CDNAME'].split()), PROVINCES[props['PRUID']], 'CA',
                 sr.shape.__geo_interface__, transform=unproject)
        if u:
            units['CA' + props['CDUID']] = u

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'units': units}, f, separators=(',', ':'))

    points = sum(len(r) for u in units.values() for r in u['rings'])
    print('%s units (%s US, %s CA), %s points, %.0f KB' % (
        len(units), sum(u['country'] == 'US' for u in units.values()),
        sum(u['country'] == 'CA' for u in units.values()), points,
        os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
