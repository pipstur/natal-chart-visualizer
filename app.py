"""
Natal Chart Explorer
---------------------
Streamlit dashboard built on top of Kerykeion.

Run with:
    streamlit run app.py

Three views on the same computed chart:
  1. Interactive wheel  - custom Plotly polar chart. Click a planet, aspect
     line, sign, or house to highlight it and see details in the side panel.
  2. Rendered chart      - Kerykeion's own crisp SVG, embedded inline.
  3. Aspect grid         - to more easily orientate your self in the aspects.
  4. Data                - sortable tables for planets, houses, aspects.
"""

import rootutils

rootutils.setup_root(__file__, [".gitignore"], pythonpath=True)

import streamlit as st
from kerykeion import ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

from config.config import (
    ALL_POSSIBLE_POINTS,
    ASPECT_STYLE,
    ASPECT_SYMBOLS,
    DEFAULT_ACTIVE_POINTS,
    PLANET_GLYPHS,
)
from utils.data import compute_subject, point_label
from utils.geocoding import do_geocode
from utils.plot import build_wheel_figure
from utils.streamlit import (
    aspect_grid_html,
    aspects_dataframe,
    houses_dataframe,
    planets_dataframe,
    render_detail_panel,
)

st.set_page_config(page_title="Natal Chart Explorer", layout="wide", page_icon="✦")

st.session_state.setdefault("lat_val", 44.804)
st.session_state.setdefault("lng_val", 20.465)
st.session_state.setdefault("tz_val", "Europe/Belgrade")
st.session_state.setdefault("resolved_place", None)
st.session_state.setdefault("geocode_error", None)

# Sidebar - birth data form
with st.sidebar:
    st.markdown("## ✦ Birth data")
    name = st.text_input("Name", "Voja")

    c1, c2, c3 = st.columns(3)
    year = c1.number_input("Year", 1, 2200, 2000)
    month = c2.number_input("Month", 1, 12, 1)
    day = c3.number_input("Day", 1, 31, 3)

    c4, c5 = st.columns(2)
    hour = c4.number_input("Hour", 0, 23, 12)
    minute = c5.number_input("Minute", 0, 59, 50)

    st.markdown("**Birthplace**")
    cs1, cs2 = st.columns([3, 1])
    cs1.text_input(
        "City search",
        key="city_query",
        placeholder="e.g. Belgrade, Serbia",
        label_visibility="collapsed",
    )
    cs2.button("🔍", on_click=do_geocode, width="stretch", help="Look up city")
    if st.session_state.geocode_error:
        st.error(st.session_state.geocode_error, icon="⚠️")
    elif st.session_state.resolved_place:
        st.caption(f"📍 {st.session_state.resolved_place}")

    lat = st.number_input("Latitude", -90.0, 90.0, key="lat_val", format="%.4f")
    lng = st.number_input("Longitude", -180.0, 180.0, key="lng_val", format="%.4f")
    tz_str = st.text_input("Timezone (IANA)", key="tz_val")

    house_system = st.selectbox(
        "House system",
        options=["P", "W", "E", "K", "R", "C", "O"],
        format_func=lambda c: {
            "P": "Placidus",
            "W": "Whole Sign",
            "E": "Equal",
            "K": "Koch",
            "R": "Regiomontanus",
            "C": "Campanus",
            "O": "Porphyry",
        }.get(c, c),
        index=0,
    )

    st.divider()
    active_points = st.multiselect(
        "Points to show",
        options=ALL_POSSIBLE_POINTS,
        default=DEFAULT_ACTIVE_POINTS,
        format_func=lambda n: f"{PLANET_GLYPHS.get(n, '')} {point_label(n)}",
        help="Lilith and the South Node are opt-in to keep the wheel from getting too busy.",
    )
    show_aspects = st.checkbox("Show aspects", value=True)
    generate = st.button("Generate chart", type="primary", width="stretch")

# Compute
if generate or "subject" not in st.session_state:
    try:
        st.session_state.subject = compute_subject(
            name, year, month, day, hour, minute, lat, lng, tz_str, house_system
        )
        st.session_state.selection = None
    except Exception as e:
        st.error(f"Couldn't compute this chart — check the inputs.\n\n`{e}`")
        st.stop()

subject = st.session_state.subject
chart_data = ChartDataFactory.create_natal_chart_data(subject)
st.session_state.setdefault("selection", None)

# Header
st.markdown(
    f"""
    <div style="padding:0.25rem 0 1rem 0;">
        <h1 style="margin-bottom:0;">{subject.name}</h1>
        <p style="color:#9a9488; margin-top:0.15rem;">
            {subject.year}-{subject.month:02d}-{subject.day:02d} · {subject.hour:02d}:{subject.minute:02d} # noqa: E501
            &nbsp;·&nbsp; {tz_str} &nbsp;·&nbsp; lat {lat:.3f}, lng {lng:.3f}
            &nbsp;·&nbsp; Ascendant <b>{subject.ascendant.sign}</b>
            &nbsp;·&nbsp; Sun <b>{subject.sun.sign}</b>
            &nbsp;·&nbsp; Moon <b>{subject.moon.sign}</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_wheel, tab_rendered, tab_aspects, tab_data = st.tabs(
    ["Interactive wheel", "Rendered chart", "Aspect grid", "Data"]
)

with tab_wheel:
    col_chart, col_info = st.columns([2.1, 1], gap="large")

    with col_chart:
        fig = build_wheel_figure(
            subject, chart_data, active_points, show_aspects, st.session_state.selection
        )
        event = st.plotly_chart(
            fig,
            key="wheel_chart",
            on_select="rerun",
            selection_mode="points",
            width=660,
            height=660,
            config={"displaylogo": False},
        )
        cclear, cnote = st.columns([1, 3])
        if cclear.button("Clear selection"):
            st.session_state.selection = None
            st.rerun()
        cnote.caption("Scroll to zoom (doesn't work currently ahhaha).")

    points = event.selection.points if event and event.selection else []
    if points:
        cd = points[0].get("customdata")
        if cd:
            new_sel = {"kind": cd[0], "key": cd[1]}
            if new_sel == st.session_state.selection:
                new_sel = None
            if new_sel != st.session_state.selection:
                st.session_state.selection = new_sel
                st.rerun()

    # with st.expander("Debug: raw selection event"):
    #     st.write("event.selection:", dict(event.selection) if event and event.selection else None) # noqa: E501
    #     st.write("stored selection:", st.session_state.selection)

    with col_info:
        render_detail_panel(subject, chart_data, active_points, st.session_state.selection)

with tab_rendered:
    drawer = ChartDrawer(chart_data=chart_data)
    svg = drawer.generate_svg_string(style="modern")
    st.iframe(
        f"<div style='width:100%; background:white;'>{svg}</div>", height=660, width="stretch"
    )
    st.download_button(
        label="💾 Save Chart",
        data=svg,
        file_name="natal_chart.svg",
        mime="image/svg+xml",
    )

with tab_aspects:
    st.subheader("Aspect grid")
    st.markdown(aspect_grid_html(chart_data, active_points), unsafe_allow_html=True)
    st.markdown("&nbsp;")
    legend = " &nbsp;·&nbsp; ".join(
        f"<span style='color:{s['color']}'>{ASPECT_SYMBOLS[a]} {a.capitalize()}</span>"
        for a, s in ASPECT_STYLE.items()
    )
    st.markdown(legend, unsafe_allow_html=True)
    st.caption("Hover a cell for the exact orb and whether it's applying or separating.")

with tab_data:
    st.subheader("Planets & points")
    st.dataframe(planets_dataframe(subject, active_points), width="content", hide_index=True)

    st.subheader("Houses")
    st.dataframe(houses_dataframe(subject), width="content", hide_index=True)

    st.subheader("Aspects")
    st.dataframe(aspects_dataframe(chart_data, active_points), width="content", hide_index=True)
