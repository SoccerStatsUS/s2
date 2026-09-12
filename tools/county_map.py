"""
Build places/counties.json, the county-grain units the closest-club territory
map colors in: US counties, Canadian census divisions, and Europe's NUTS 3
regions. Each unit carries the country code the map filters on.

Sources, all public domain or open with attribution:

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

  Eurostat GISCO, NUTS 2021, level 3, 1:3M, WGS84 GeoJSON. (c) EuroGeographics
  for the administrative boundaries.
  https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_03M_2021_4326_LEVL_3.geojson
  NUTS 3 is the county analogue across Europe: Kreise, provinces,
  departements, UK counties and unitary authorities. The whole file is kept,
  every country, so any European league can draw a map. The 2021 edition is
  the last with the United Kingdom in it, which the map splits into its four
  football countries by NUTS 1 code, as places/world.json does.

  geoBoundaries (William & Mary geoLab), gbOpen release, ADM2, simplified
  GeoJSON, CC BY 4.0. One file per country; the API at
  https://www.geoboundaries.org/api/current/gbOpen/<ISO3>/ADM2/ names the
  current download under simplifiedGeometryGeoJSON. Mexico's municipios come
  from here (2,457, the World Bank's 2012 set), as do the seven Central
  American countries (Guatemala, Belize, Honduras, El Salvador, Nicaragua,
  Costa Rica, Panama; the sources behind each are named in the API record,
  Nicaragua's being OpenStreetMap under the ODbL). The rest of Latin America
  can follow the same way: pass --adm2 once per country as CODE=path, where
  CODE is the atlas country code the map filters on.

The two shapefiles need a reader the site does not otherwise want:

    uv pip install -p .venv/bin/python pyshp
    .venv/bin/python tools/county_map.py --us cb_2020_us_county_20m.shp \\
        --ca lcd_000b21a_e.shp --eu NUTS_RG_03M_2021_4326_LEVL_3.geojson \\
        --adm2 MX=geoBoundaries-MEX-ADM2_simplified.geojson
"""

import argparse
import json
import math
import os
import sys

import shapefile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from world_map import extent, rings, simplify  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'places', 'counties.json')

# Degrees. About a pixel when a continent fills a thousand of them; finer
# than that is coastline the map cannot draw, and there are 5,000 units.
TOLERANCE = 0.012

# Units centred north of 60 degrees -- the three territories -- are outside
# any frame the map draws, so they are kept for the table and thinned to a
# sketch. Nunavut alone was a third of the file at the finer tolerance.
NORTH = 60.0
NORTH_TOLERANCE = 0.08

# Rings smaller than this in bounding-box degrees are dropped unless they are
# all a unit has. Islands cost points and color nothing anyone can see.
MIN_RING = 0.08

# Puerto Rico and the island territories: in the county file, in no MLS map.
SKIP_STATES = {'60', '66', '69', '72', '78'}

# France's overseas departements sit in the Caribbean, South America and the
# Indian Ocean; a Ligue 1 map would count them and never draw them.
SKIP_NUTS = ('FRY',)

PROVINCES = {
    '10': 'NL', '11': 'PE', '12': 'NS', '13': 'NB', '24': 'QC', '35': 'ON',
    '46': 'MB', '47': 'SK', '48': 'AB', '59': 'BC', '60': 'YT', '61': 'NT',
    '62': 'NU',
}

# NUTS 1 codes of the United Kingdom, by football country.
HOME_NATIONS = {'UKL': 'WLS', 'UKM': 'SCT', 'UKN': 'NIR'}


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
    theta = math.atan2(x, y) if N > 0 else math.atan2(-x, -y)
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
        elif not i:
            # A caye or islet smaller than the tolerance: keep the unit as
            # its bounding rectangle so it still counts and draws as a speck.
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            x0, x1 = round(min(xs), 3), round(max(xs), 3)
            y0, y1 = round(min(ys), 3), round(max(ys), 3)
            if x1 - x0 < 0.001:
                x1 = x0 + 0.001
            if y1 - y0 < 0.001:
                y1 = y0 + 0.001
            kept.append([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])

    if not kept:
        return None

    # A unit a couple of kilometres across simplifies to a sliver whose
    # rounded outline can miss the true centroid by metres; keep the point
    # inside what is drawn.
    xs = [p[0] for ring in kept for p in ring]
    ys = [p[1] for ring in kept for p in ring]
    lon = min(max(lon, min(xs)), max(xs))
    lat = min(max(lat, min(ys)), max(ys))

    return {'name': name, 'state': state, 'country': country,
            'lon': round(lon, 4), 'lat': round(lat, 4), 'rings': kept}


# ---- Sources ------------------------------------------------------------
#
# Each yields (id, unit). Ids carry the source's prefix so no two can meet.

def census_counties(path):
    for sr in shapefile.Reader(path).iterShapeRecords():
        props = sr.record.as_dict()
        if props['STATEFP'] in SKIP_STATES:
            continue
        u = unit(props['NAME'], props['STUSPS'], 'US', sr.shape.__geo_interface__)
        if u:
            yield 'US' + props['GEOID'], u


def statcan_divisions(path):
    for sr in shapefile.Reader(path, encoding='latin-1').iterShapeRecords():
        props = sr.record.as_dict()
        u = unit(' '.join(props['CDNAME'].split()), PROVINCES[props['PRUID']], 'CA',
                 sr.shape.__geo_interface__, transform=unproject)
        if u:
            yield 'CA' + props['CDUID'], u


def gisco_nuts3(path):
    with open(path, encoding='utf-8') as f:
        features = json.load(f)['features']

    for feature in features:
        props = feature['properties']
        code = props['NUTS_ID']
        if code.startswith(SKIP_NUTS):
            continue
        country = props['CNTR_CODE']
        if country == 'UK':
            country = HOME_NATIONS.get(code[:3], 'ENG')
        # The NUTS 1 code stands where a state or province would: a German
        # Land, a French region, an English region.
        u = unit(props['NAME_LATN'], code[:3], country, feature['geometry'])
        if u:
            yield 'EU' + code, u


def geoboundaries_adm2(path, country):
    """
    A geoBoundaries ADM2 file for one country. The features carry no parent
    unit, so state is left blank; ids are the country code and the
    boundary's own shapeID.
    """
    with open(path, encoding='utf-8') as f:
        features = json.load(f)['features']

    for feature in features:
        props = feature['properties']
        u = unit(props['shapeName'], '', country, feature['geometry'])
        if u:
            yield country + props['shapeID'], u


def build(sources):
    units = {}
    for reader, path in sources:
        for uid, u in reader(path):
            units[uid] = u

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'units': units}, f, separators=(',', ':'))

    by_country = {}
    for u in units.values():
        by_country[u['country']] = by_country.get(u['country'], 0) + 1
    points = sum(len(r) for u in units.values() for r in u['rings'])
    print('%s units, %s points, %.0f KB' % (len(units), points, os.path.getsize(OUT) / 1024))
    print(' '.join('%s:%s' % kv for kv in sorted(by_country.items())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--us', required=True, help='Census cb_2020_us_county_20m.shp')
    parser.add_argument('--ca', required=True, help='Statistics Canada lcd_000b21a_e.shp')
    parser.add_argument('--eu', required=True, help='GISCO NUTS_RG_03M_2021_4326_LEVL_3.geojson')
    parser.add_argument('--adm2', action='append', default=[], metavar='CODE=PATH',
                        help='a geoBoundaries ADM2 simplified GeoJSON, e.g. MX=...MEX-ADM2_simplified.geojson')
    args = parser.parse_args()

    sources = [(census_counties, args.us), (statcan_divisions, args.ca), (gisco_nuts3, args.eu)]
    for spec in args.adm2:
        code, path = spec.split('=', 1)
        sources.append((lambda p, code=code: geoboundaries_adm2(p, code), path))
    build(sources)
