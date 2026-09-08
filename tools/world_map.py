"""
Build places/world.json, the country outlines the minutes map draws.

Source: Natural Earth 1:50m admin_0 map subunits, public domain.
https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_map_subunits.geojson

Subunits rather than countries because this is a soccer site: England,
Scotland, Wales and Northern Ireland are separate football countries and have
to shade separately, as do Guadeloupe and Martinique. The 1:10m and 1:110m
sets are the wrong size in both directions -- 110m drops the whole Caribbean,
including Saint Kitts and Nevis.

Run when the source changes:

    python tools/world_map.py ne_50m_admin_0_map_subunits.geojson
"""

import json
import os
import sys
import unicodedata


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'places', 'world.json')

# Degrees. Small enough to keep the Caribbean islands legible when the map
# crops to them, coarse enough to keep the file under a megabyte.
TOLERANCE = 0.04

# Rings smaller than this in bounding-box degrees are dropped unless the
# subunit has nothing bigger -- offshore rocks cost bytes and draw nothing,
# but Saint Kitts is a country.
MIN_RING = 0.05

# Not a birth country in any bio, and a quarter of the world's land area.
SKIP = {'ATA'}

# Countries the bios record that Natural Earth files under another name, and
# states that no longer exist. Historical states shade their principal
# successor; the table beside the map keeps the recorded name.
ALIASES = {
    'cape verde': ['CPV'],
    'macedonia': ['MKD'],
    'czechoslovakia': ['CZE'],
    'east germany': ['DEU'],
    'west germany': ['DEU'],
    'yugoslavia': ['SRB'],
    'zaire': ['COD'],
}

# Natural Earth splits these out of the United Kingdom, and football keeps
# them split. Every other subunit without its own ISO code -- Alaska, Hawaii,
# Corsica -- belongs to its parent country.
HOME_NATIONS = {'ENG', 'SCT', 'WLS', 'NIR'}

NAME_FIELDS = ('NAME', 'NAME_LONG', 'GEOUNIT', 'SUBUNIT', 'BRK_NAME',
               'NAME_CIAWF', 'NAME_SORT')


def normalize(name):
    name = unicodedata.normalize('NFKD', name or '').encode('ascii', 'ignore').decode()
    return name.lower().replace('.', '').replace('-', ' ').replace("'", '').strip()


def simplify(points, tolerance):
    """Douglas-Peucker, iterative so a long coastline cannot blow the stack."""
    if len(points) < 3:
        return points

    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]

    while stack:
        start, end = stack.pop()
        ax, ay = points[start]
        bx, by = points[end]
        dx, dy = bx - ax, by - ay
        span = dx * dx + dy * dy

        worst, worst_i = 0.0, None
        for i in range(start + 1, end):
            px, py = points[i]
            if span:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / span))
                qx, qy = ax + t * dx, ay + t * dy
            else:
                qx, qy = ax, ay
            d = (px - qx) ** 2 + (py - qy) ** 2
            if d > worst:
                worst, worst_i = d, i

        if worst_i is not None and worst > tolerance * tolerance:
            keep[worst_i] = True
            stack.append((start, worst_i))
            stack.append((worst_i, end))

    return [p for p, k in zip(points, keep) if k]


def rings(geometry):
    if geometry['type'] == 'Polygon':
        polygons = [geometry['coordinates']]
    else:
        polygons = geometry['coordinates']

    # Outer ring only. Lakes and enclaves do not carry data here, and the
    # holes cost as much as the coastlines that do.
    return [polygon[0] for polygon in polygons if polygon]


def extent(ring):
    xs = [x for x, y in ring]
    ys = [y for x, y in ring]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def football_country(props):
    """
    The key subunits group under. A subunit stands alone when football treats
    it separately -- a home nation, or an overseas territory carrying its own
    ISO code, like Martinique. Everything else rolls up into its parent, so
    Alaska and Hawaii shade with the rest of the United States.
    """
    code = props['SU_A3']
    if code in HOME_NATIONS:
        return code

    iso = props.get('ISO_A3')
    parent = props.get('ADM0_A3')
    if iso and iso != '-99' and iso != parent:
        return code

    return parent or code


def build(source):
    features = json.load(open(source, encoding='utf-8'))['features']

    shapes = {}
    groups = {}

    for feature in features:
        props = feature['properties']
        code = props.get('SU_A3')
        if not code or code in SKIP:
            continue

        kept = []
        for ring in rings(feature['geometry']):
            simplified = [[round(x, 2), round(y, 2)] for x, y in simplify(ring, TOLERANCE)]
            if len(simplified) >= 3:
                kept.append(simplified)

        if not kept:
            continue

        kept.sort(key=extent, reverse=True)
        shapes[code] = [kept[0]] + [r for r in kept[1:] if extent(r) >= MIN_RING]
        groups.setdefault(football_country(props), []).append((props, kept[0]))

    names = {}
    for members in groups.values():
        # Name the group after its largest piece: the United States by the
        # lower 48 rather than by Alaska.
        members.sort(key=lambda m: extent(m[1]), reverse=True)
        codes = [props['SU_A3'] for props, _ in members]
        biggest = members[0][0]

        keys = {normalize(biggest.get(field)) for field in NAME_FIELDS}
        if len(members) > 1:
            keys.add(normalize(biggest.get('ADMIN')))

        for key in keys:
            if key:
                names.setdefault(key, codes)

    names.update(ALIASES)

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'shapes': shapes, 'names': names}, f, separators=(',', ':'))

    points = sum(len(r) for rs in shapes.values() for r in rs)
    print('%s subunits, %s names, %s points, %.0f KB'
          % (len(shapes), len(names), points, os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    build(sys.argv[1])
