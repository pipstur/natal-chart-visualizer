import rootutils

rootutils.setup_root(__file__, [".gitignore"], pythonpath=True)

import math

from kerykeion import AstrologicalSubjectFactory

from config.config import HOUSE_NAME_TO_NUM, HOUSE_ORDINAL_WORDS, SIGN_GLYPHS


def compute_subject(name, year, month, day, hour, minute, lat, lng, tz_str, house_system):
    return AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        lng=lng,
        lat=lat,
        tz_str=tz_str,
        online=False,
        houses_system_identifier=house_system,
    )


def point_data(subject, point_name):
    """Fetch a computed point (planet/angle/node) off the subject by its Kerykeion name."""
    return getattr(subject, point_name.lower())


def house_cusps(subject):
    names = [f"{w.lower()}_house" for w in HOUSE_ORDINAL_WORDS]
    return [getattr(subject, n) for n in names]


def wrap_delta(a, b):
    """Shortest signed angular distance a -> b, in degrees."""
    return (b - a + 180) % 360 - 180


def chord_points(r1, theta1_deg, r2, theta2_deg, n=9):
    """N points evenly spaced along the *straight* chord between two polar
    coordinates, returned as (r_list, theta_list).

    A Scatterpolar line with only 2 vertices renders fine visually (Plotly
    draws a straight segment between any two points), but Plotly's click
    selection is tied to actual data-point vertices - clicking mid-line, far
    from either endpoint, may not land on a selectable point even though
    hover (which interpolates continuously along the rendered path) works
    fine there. Adding real vertices along the line fixes that. We interpolate
    in plain Cartesian space (assuming rotation=0) rather than at fixed r
    with interpolated theta, since the latter would bow the line into an arc
    instead of keeping it straight.
    """
    x1, y1 = r1 * math.cos(math.radians(theta1_deg)), r1 * math.sin(math.radians(theta1_deg))
    x2, y2 = r2 * math.cos(math.radians(theta2_deg)), r2 * math.sin(math.radians(theta2_deg))
    rs, thetas = [], []
    for i in range(n):
        t = i / (n - 1)
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        rs.append(math.hypot(x, y))
        thetas.append(math.degrees(math.atan2(y, x)) % 360)
    return rs, thetas


def house_num_of(point):
    """Map a computed point's `.house` field (e.g. 'Ninth_House') to 1-12."""
    return HOUSE_NAME_TO_NUM.get(str(point.house)) if point.house else None


def format_dms(deg_float):
    """41.7305 -> 41° 43' 50\" """
    sign = "-" if deg_float < 0 else ""
    deg_float = abs(deg_float)
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60)
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
    return f"{sign}{d}° {m}' {s}\""


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def aspect_key(asp):
    return f"{asp.p1_name}__{asp.aspect}__{asp.p2_name}"


def visible_aspects(chart_data, active_points):
    return [
        a for a in chart_data.aspects if a.p1_name in active_points and a.p2_name in active_points
    ]


def find_aspect(chart_data, active_points, key):
    for asp in visible_aspects(chart_data, active_points):
        if aspect_key(asp) == key:
            return asp
    return None


def point_label(name):
    return name.replace("_", " ")


def point_position_str(p):
    return f"{format_dms(p.position)} {SIGN_GLYPHS[p.sign_num]} {p.sign}"


def point_house_str(p):
    n = house_num_of(p)
    return f"{ordinal(n)} house" if n else "—"
