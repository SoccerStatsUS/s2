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

    # Premier League, 1992-. Club colors; white-kit clubs take their trim (Leeds' gold, Spurs' navy, Swansea's black).
    'arsenal': '#ef0107',
    'aston-villa': '#670e36',
    'barnsley': '#8f1030',
    'birmingham-city': '#1f4fd1',
    'blackburn-rovers': '#009ee0',
    'blackpool-fc': '#f68712',
    'bolton-wanderers': '#3949ab',
    'bradford-city': '#5d4037',
    'burnley': '#6c1d45',
    'cardiff-city': '#0070b5',
    'charlton-athletic': '#d4021d',
    'chelsea': '#034694',
    'coventry-city': '#b3e5fc',
    'crystal-palace': '#c4122e',
    'derby-county': '#808080',
    'everton': '#003399',
    'fulham': '#222222',
    'hull-city': '#f5a12d',
    'ipswich-town': '#5c6bc0',
    'leeds-united': '#ffcd00',
    'leicester-city': '#2d7fd0',
    'liverpool': '#c81022',
    'manchester-city': '#6cabdd',
    'manchester-united': '#da291c',
    'middlesbrough': '#9b1120',
    'newcastle-united': '#241f20',
    'norwich-city': '#ffd500',
    'nottingham-forest': '#a8001c',
    'oldham-athletic': '#f0a030',
    'portsmouth': '#1e88e7',
    'queens-park-rangers': '#1d5ba4',
    'reading': '#6dd5ed',
    'sheffield-united': '#ee2737',
    'sheffield-wednesday': '#0e63ad',
    'southampton': '#ff1744',
    'stoke-city': '#d9534f',
    'sunderland': '#ff6f61',
    'swansea-city': '#4a4a4a',
    'swindon-town': '#b71c1d',
    'tottenham-hotspur': '#132257',
    'watford': '#fbee23',
    'west-bromwich-albion': '#1c2f5a',
    'west-ham-united': '#7a263a',
    'wigan-athletic': '#8cc8ff',
    'wimbledon-fc': '#ffb000',
    'wolves': '#d99a1a',

    # Bundesliga, 1995-. Nuremberg has two slugs in the data and one color.
    '1-fc-kaiserslautern': '#e30613',
    '1-fc-koln': '#9b0f1f',
    '1-fc-nuremberg': '#7b0e2a',
    '1-fc-nurnberg': '#7b0e2b',
    '1899-hoffenheim': '#1c63b7',
    'alemannia-aachen': '#ffd800',
    'arminia-bielefeld': '#343434',
    'bayer-leverkusen': '#ff5253',
    'borussia-dortmund': '#fde100',
    'borussia-monchengladbach': '#5cb85c',
    'eintracht-braunschweig': '#0033a0',
    'eintracht-frankfurt': '#101010',
    'energie-cottbus': '#ef5350',
    'fc-augsburg': '#1b7f3c',
    'fc-bayern-munich': '#dc052d',
    'fc-st-pauli': '#624a2e',
    'fortuna-dusseldorf': '#f28b82',
    'hamburger-sv': '#0a3f86',
    'hannover-96': '#b5d334',
    'hansa-rostock': '#a7d8f5',
    'hertha-bsc': '#1e6fd9',
    'kfc-uerdingen': '#f6a801',
    'karlsruher-sc': '#4a90e2',
    'msv-duisburg': '#7fa8d8',
    'mainz-05': '#c2185b',
    'sc-freiburg': '#b3b3b3',
    'ssv-ulm-1846': '#3a3a3a',
    'schalke-04': '#004e9e',
    'spvgg-greuther-furth': '#7cc47f',
    'spvgg-unterhaching': '#f5a624',
    'tsv-1860-munchen': '#64a0dc',
    'vfb-stuttgart': '#ff8a65',
    'vfl-bochum': '#1e90e0',
    'vfl-wolfsburg': '#65b32e',
    'werder-bremen': '#1d9053',

    # La Liga, 1995-. Real Madrid's white is drawn as its gold trim; Valencia's as its orange.
    'albacete': '#8b8b00',
    'almeria': '#d21e2b',
    'athletic-bilbao': '#ee2523',
    'atletico-madrid': '#cb3524',
    'cd-logrones': '#7a1213',
    'cf-extremadura': '#1d4f9c',
    'celta-vigo': '#8ac3ee',
    'cadiz': '#ffd200',
    'deportivo-alaves': '#0761af',
    'deportivo-la-coruna': '#004b9b',
    'elche-cf': '#007b3d',
    'fc-barcelona': '#a2004f',
    'getafe': '#3d9be9',
    'gimnastic-de-tarragona': '#5c0f2a',
    'granada-cf': '#8a0a12',
    'hercules-cf': '#1a4fa0',
    'levante': '#7e1e3a',
    'mallorca': '#e0121a',
    'malaga': '#1e88e5',
    'merida': '#333333',
    'numancia': '#b5651d',
    'osasuna': '#0f2a5e',
    'rcd-espanyol': '#0068b3',
    'racing-de-santander': '#1f7a3c',
    'rayo-vallecano': '#e53935',
    'real-betis': '#00954c',
    'real-madrid': '#cfb53b',
    'real-murcia': '#b8112a',
    'real-oviedo': '#4d8fd6',
    'real-sociedad': '#2196f3',
    'real-valladolid': '#6f2c91',
    'real-zaragoza': '#1c4f9c',
    'recreativo-huelva': '#4fa3e3',
    'sd-compostela': '#7fb2e0',
    'sevilla-fc': '#d42a30',
    'sporting-de-gijon': '#9e1030',
    'tenerife': '#1e5fbf',
    'ud-las-palmas': '#ffd801',
    'ud-salamanca': '#7d7d7d',
    'valencia-cf': '#f39200',
    'villarreal': '#ffe667',
    'xerez': '#2b5db0',

    # Serie A, 1996-.
    'ac-milan': '#fb090b',
    'ac-reggiana-1919': '#8b1a2b',
    'afc-fiorentina': '#5b2c8f',
    'ancona': '#f26d6d',
    'ascoli': '#8c8c8c',
    'atalanta': '#2962ff',
    'bari': '#1a1a1c',
    'bologna': '#cf1b2f',
    'brescia-calcio': '#4f8fdf',
    'cagliari': '#b21e2e',
    'catania': '#cc2027',
    'cesena': '#a0a0a0',
    'chievo': '#b8860b',
    'como': '#7fb8ea',
    'empoli': '#1565c0',
    'genoa': '#7a1224',
    'inter-milan': '#0a3f8f',
    'juventus': '#1f1f1f',
    'lazio': '#87d8f7',
    'lecce': '#ffcc00',
    'livorno': '#d81b60',
    'messina': '#e8b400',
    'modena-fc': '#ff8c00',
    'napoli': '#12a0d7',
    'novara': '#7ec8ff',
    'palermo': '#f3a5b7',
    'parma-fc': '#e0e0e0',
    'perugia': '#8e0000',
    'pescara': '#2a68c1',
    'piacenza': '#cf2030',
    'reggina-calcio': '#5a0f1f',
    'roma': '#9a1f40',
    'salernitana': '#4a1030',
    'sampdoria': '#6fa8dc',
    'siena': '#303030',
    'torino-fc': '#a83a5a',
    'treviso': '#1c5aa5',
    'us-sassuolo': '#009a3e',
    'udinese': '#3b3b3b',
    'venezia': '#f37021',
    'verona': '#ffe500',
    'vicenza-calcio': '#8b0a1e',

    # Ligue 1, 1995-.
    'as-nancy': '#a50021',
    'ajaccio': '#e57373',
    'arles-avignon': '#f3c000',
    'auxerre': '#8fb3e8',
    'bastia': '#2a5db6',
    'berrichonne': '#b71c1c',
    'bordeaux': '#0f1f6b',
    'boulogne': '#b3202c',
    'brest': '#ff4d6d',
    'caen': '#003b6f',
    'cannes': '#f08080',
    'dijon-fco': '#6d4c41',
    'evian-tg': '#e83e8c',
    'fc-istres': '#6a2c91',
    'fc-lorient': '#f36f21',
    'fc-sochaux': '#f7c600',
    'grenoble': '#1c62b9',
    'gueugnon': '#556b2f',
    'guingamp': '#6d0b14',
    'le-havre': '#7ab4e0',
    'le-mans': '#ff8c01',
    'lens': '#f3c300',
    'lille-osc': '#d81e2c',
    'lyon': '#4fa3e0',
    'marseille': '#009de0',
    'martigues': '#1a6fc0',
    'metz': '#5e0f2a',
    'monaco': '#d20a2e',
    'montpellier-herault-sc': '#f47a20',
    'nantes': '#ffd300',
    'ogc-nice': '#2a2a2a',
    'paris-saint-germain': '#1f4ec2',
    'rc-strasbourg': '#0d2a6b',
    'reims': '#ff5c8a',
    'rennes': '#151515',
    'saint-etienne': '#1d8a3a',
    'sedan': '#2e8b3d',
    'toulouse': '#5a2d8a',
    'troyes': '#40c4ff',
    'valenciennes-fc': '#e05a5a',

    # Liga MX, 1943-. Mexico City, Guadalajara and Monterrey are shared territories and stripe.
    'albinegros-de-orizaba': '#3a3a3b',
    'atlante': '#1d4b9e',
    'atlas': '#212122',
    'atletico-celaya': '#795548',
    'atletico-espanol': '#19418e',
    'atletico-potosino': '#7e57c2',
    'cd-guadalajara': '#cc1a2b',
    'cd-marte-mexico': '#1f8a4c',
    'cd-oro': '#c9a227',
    'cf-asturias': '#1a237e',
    'cf-ciudad-madero': '#ffb74d',
    'cf-monterrey': '#4169e1',
    'cf-oaxtepec': '#7a3fa0',
    'celaya': '#6a1b9a',
    'club-america': '#f9d020',
    'club-deportivo-zamora': '#ffab40',
    'club-jalisco': '#6a9a23',
    'club-leon': '#007a4d',
    'club-tijuana': '#c9242d',
    'cobras-de-ciudad-juarez': '#2c2c2c',
    'cobras-de-queretaro': '#d5a018',
    'colibries-de-morelos': '#0aa1a0',
    'correcaminos-uat': '#f27a1a',
    'cruz-azul': '#0d47a1',
    'cuautla-fc': '#8b5a2b',
    'deportivo-neza': '#d03a2a',
    'dorados-de-sinaloa': '#b8860c',
    'indios-de-ciudad-juarez': '#b31b2b',
    'irapuato': '#f28c8c',
    'jaguares-de-chiapas': '#f36f24',
    'la-piedad': '#1a4fa6',
    'laguna-fc': '#a5d6a7',
    'madero': '#3a7bd5',
    'moctezuma-de-orizaba': '#2e7d32',
    'monarcas-morelia': '#e91e63',
    'nacional-de-guadalajara': '#ff7043',
    'necaxa': '#a40000',
    'nuevo-leon': '#2ea44f',
    'pachuca': '#64b5f6',
    'puebla': '#9ecbf0',
    'queretaro-fc': '#546e7a',
    'real-club-espana': '#e2a020',
    'san-luis-fc': '#26c6da',
    'san-sebastian-de-leon': '#90caf9',
    'santos-laguna': '#4caf50',
    'tampico-madero-fc': '#00838f',
    'tecos': '#f57c00',
    'toluca': '#8e0a14',
    'toros-neza': '#8d6e63',
    'torreon-fc': '#1f4faa',
    'uanl': '#ffb300',
    'unam': '#1a2c56',
    'universidad-de-guadalajara': '#fff176',
    'union-de-curtidores': '#ce93d8',
    'veracruz': '#ff5252',
    'zacatepec': '#66bb6a',
    'angeles-de-puebla': '#5b3fa0',
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
LABEL_HEIGHT = 8
LABEL_GLYPH = 3.2


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
