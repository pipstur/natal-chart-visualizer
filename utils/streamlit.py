import rootutils

rootutils.setup_root(__file__, [".gitignore"], pythonpath=True)

import pandas as pd
import streamlit as st

from config.config import ASPECT_STYLE, ASPECT_SYMBOLS, PLANET_GLYPHS, SIGN_GLYPHS, SIGN_NAMES
from utils.data import (
    find_aspect,
    format_dms,
    house_cusps,
    ordinal,
    point_data,
    point_house_str,
    point_label,
    point_position_str,
    visible_aspects,
)


def render_point_card(subject, name):
    p = point_data(subject, name)
    glyph = PLANET_GLYPHS.get(name, "")
    retro = " (R)" if getattr(p, "retrograde", False) else ""
    st.markdown(f"**{glyph} {point_label(name)}{retro}**  \n*{subject.name}*")
    st.markdown(f"{point_position_str(p)} · {point_house_str(p)}")


def render_detail_panel(subject, chart_data, active_points, selection):
    if selection is None:
        st.caption("Click a planet, aspect line, or sign on the wheel to see details here.")
        return

    kind, key = selection["kind"], selection["key"]

    if kind == "aspect":
        asp = find_aspect(chart_data, active_points, key)
        if asp is None:
            st.caption("That aspect is no longer available.")
            return
        symbol = ASPECT_SYMBOLS.get(asp.aspect, "")
        st.markdown(f"### {symbol} {asp.aspect.capitalize()}")
        st.markdown(
            f"**Exact angle** {asp.aspect_degrees}°  \n"
            f"**Orb** {format_dms(asp.orbit)}  \n"
            f"**Movement** {asp.aspect_movement}"
        )
        st.divider()
        render_point_card(subject, asp.p1_name)
        st.markdown("&nbsp;")
        render_point_card(subject, asp.p2_name)

    elif kind == "planet":
        st.markdown("### Point")
        render_point_card(subject, key)
        involved = [
            a for a in visible_aspects(chart_data, active_points) if key in (a.p1_name, a.p2_name)
        ]
        if involved:
            st.divider()
            st.markdown("**Aspects**")
            for a in involved:
                other = a.p2_name if a.p1_name == key else a.p1_name
                sym = ASPECT_SYMBOLS.get(a.aspect, "")
                st.markdown(f"{sym} {a.aspect} {point_label(other)} · orb {format_dms(a.orbit)}")

    elif kind == "sign":
        st.markdown(f"### {SIGN_GLYPHS[key]} {SIGN_NAMES[key]}")
        members = [n for n in active_points if point_data(subject, n).sign_num == key]
        if not members:
            st.caption("No planets or points fall in this sign.")
        for n in members:
            render_point_card(subject, n)
            st.markdown("&nbsp;")


def planets_dataframe(subject, active_points):
    rows = []
    for name in active_points:
        p = point_data(subject, name)
        rows.append(
            {
                "Point": f"{PLANET_GLYPHS.get(name, '')} {point_label(name)}",
                "Sign": f"{SIGN_GLYPHS[p.sign_num]} {p.sign}",
                "Degree": format_dms(p.position),
                "House": point_house_str(p),
                "℞": "℞" if bool(getattr(p, "retrograde", False)) else "",
                "Speed °/day": round(p.speed, 3),
            }
        )
    return pd.DataFrame(rows)


def houses_dataframe(subject):
    rows = []
    for i, cusp in enumerate(house_cusps(subject), start=1):
        rows.append(
            {
                "House": ordinal(i),
                "Sign": f"{SIGN_GLYPHS[cusp.sign_num]} {cusp.sign}",
                "Cusp": format_dms(cusp.position),
            }
        )
    return pd.DataFrame(rows)


def aspects_dataframe(chart_data, active_points):
    rows = []
    for asp in visible_aspects(chart_data, active_points):
        rows.append(
            {
                "A": f"{PLANET_GLYPHS.get(asp.p1_name, '')} {point_label(asp.p1_name)}",
                "Aspect": f"{ASPECT_SYMBOLS.get(asp.aspect, '')} {asp.aspect.capitalize()}",
                "B": f"{PLANET_GLYPHS.get(asp.p2_name, '')} {point_label(asp.p2_name)}",
                "Orb": format_dms(asp.orbit),
                "Movement": asp.aspect_movement,
            }
        )
    return pd.DataFrame(rows)


def aspect_grid_html(chart_data, active_points):
    """A classic astrology 'aspectarian' - lower-triangle grid, one row/column
    per visible point, cell colored and symbolized by aspect type where one
    exists between that pair."""
    lookup = {}
    for asp in visible_aspects(chart_data, active_points):
        lookup[frozenset((asp.p1_name, asp.p2_name))] = asp

    css = """
    <style>
    table.aspgrid { border-collapse: collapse; }
    table.aspgrid th, table.aspgrid td {
        width: 34px; height: 34px; text-align: center; vertical-align: middle;
        border: 1px solid #2a2f3a; font-size: 15px; padding: 0;
    }
    table.aspgrid th {
        background: #15181e; color: #c9c4b8; font-size: 16px; font-weight: 400;
    }
    </style>
    """
    rows_html = ["<table class='aspgrid'><tr><th></th>"]
    for p in active_points:
        rows_html.append(f"<th title='{point_label(p)}'>{PLANET_GLYPHS.get(p, '')}</th>")
    rows_html.append("</tr>")

    for i, p1 in enumerate(active_points):
        rows_html.append(f"<tr><th title='{point_label(p1)}'>{PLANET_GLYPHS.get(p1, '')}</th>")
        for j, p2 in enumerate(active_points):
            if j >= i:
                rows_html.append("<td></td>")
                continue
            asp = lookup.get(frozenset((p1, p2)))
            if asp:
                style = ASPECT_STYLE.get(asp.aspect, dict(color="#888888"))
                color = style["color"]
                sym = ASPECT_SYMBOLS.get(asp.aspect, "?")
                title = (
                    f"{point_label(p1)} {asp.aspect} {point_label(p2)} · "
                    f"orb {format_dms(asp.orbit)} · {asp.aspect_movement}"
                )
                rows_html.append(
                    f"<td style='background:{color}2e; color:{color}; font-weight:600;' "
                    f'title="{title}">{sym}</td>'
                )
            else:
                rows_html.append("<td></td>")
        rows_html.append("</tr>")
    rows_html.append("</table>")
    return css + "".join(rows_html)
