import rootutils

rootutils.setup_root(__file__, [".gitignore"], pythonpath=True)

import plotly.graph_objects as go

from config.config import (
    ASPECT_STYLE,
    ASPECT_SYMBOLS,
    CHART_BG,
    GOLD,
    GRID_COLOR,
    PAPER_BG,
    PLANET_GLYPHS,
    R_ANGLE_LABEL,
    R_ANGLE_LINE,
    R_ASPECT,
    R_HOUSE_NUM,
    R_PLANET_BASE,
    R_PLANET_STEP,
    R_SIGN_BASE,
    R_SIGN_LABEL,
    R_SIGN_TOP,
    RADIAL_MAX,
    SIGN_GLYPHS,
    SIGN_NAMES,
    TEXT_COLOR,
)
from utils.data import (
    aspect_key,
    chord_points,
    format_dms,
    house_cusps,
    point_data,
    point_house_str,
    point_label,
    point_position_str,
    visible_aspects,
    wrap_delta,
)


def build_wheel_figure(subject, chart_data, active_points, show_aspects, selection):
    """selection: None or {"kind": "aspect"|"planet"|"sign", "key": ...}"""
    asc_deg = subject.ascendant.abs_pos
    # Rotate so the Ascendant sits on the left (9 o'clock), zodiac longitude
    # increasing counter-clockwise, matching the conventional wheel layout.
    rotation = 180 - asc_deg
    sel_kind = selection["kind"] if selection else None
    sel_key = selection["key"] if selection else None

    fig = go.Figure()
    cusps = house_cusps(subject)

    # --- zodiac sign wedges (background, clickable) -------------------------
    for i in range(12):
        start = i * 30
        mid = start + 15
        active = sel_kind == "sign" and sel_key == i
        base_shade = 0.05 if i % 2 == 0 else 0.0
        fig.add_trace(
            go.Barpolar(
                r=[R_SIGN_TOP],
                theta=[mid],
                width=[30],
                base=R_SIGN_BASE,
                marker=dict(
                    color=(
                        "rgba(217,184,119,0.35)" if active else f"rgba(255,255,255,{base_shade})"
                    ),
                    line=dict(color=GRID_COLOR, width=1),
                ),
                customdata=[["sign", i]],
                hovertext=[SIGN_NAMES[i]],
                hoverinfo="text",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[R_SIGN_LABEL],
                theta=[mid],
                mode="text",
                text=[SIGN_GLYPHS[i]],
                textfont=dict(size=16, color="#c9c4b8" if not active else GOLD),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # --- house cusp lines + numbers ------------------------------------------
    for idx, cusp in enumerate(cusps):
        deg = cusp.abs_pos
        next_deg = cusps[(idx + 1) % 12].abs_pos
        mid_deg = deg + (wrap_delta(deg, next_deg) % 360) / 2
        fig.add_trace(
            go.Scatterpolar(
                r=[0, R_SIGN_BASE],
                theta=[deg, deg],
                mode="lines",
                line=dict(color=GRID_COLOR, width=1.5 if idx in (0, 3, 6, 9) else 0.7),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[R_HOUSE_NUM],
                theta=[mid_deg],
                mode="text",
                text=[str(idx + 1)],
                textfont=dict(size=11, color="#6f7580"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # --- aspect lines (chords between points) --------------------------------
    highlighted_points = set()
    if show_aspects:
        dim_all_aspects = sel_kind == "sign"
        for asp in visible_aspects(chart_data, active_points):
            key = aspect_key(asp)
            style = ASPECT_STYLE.get(asp.aspect, dict(color="#666666", dash="solid"))
            is_selected = sel_kind == "aspect" and sel_key == key
            touches_selected_planet = sel_kind == "planet" and sel_key in (
                asp.p1_name,
                asp.p2_name,
            )
            if is_selected:
                highlighted_points.update([asp.p1_name, asp.p2_name])
            if selection is None:
                opacity, width = 0.65, 2.0
            elif is_selected:
                opacity, width = 1.0, 3.4
            elif touches_selected_planet:
                opacity, width = 0.85, 2.4
            elif dim_all_aspects:
                opacity, width = 0.05, 1.4
            else:
                opacity, width = 0.08, 1.4
            hover_text = (
                f"{point_label(asp.p1_name)} {ASPECT_SYMBOLS.get(asp.aspect,'')} "
                f"{asp.aspect} {point_label(asp.p2_name)} "
                f"(orb {format_dms(asp.orbit)}, {asp.aspect_movement})"
            )
            # Invisible, much thicker line laid under the visible one, densified
            # with real intermediate vertices (not just the 2 endpoints) so a
            # click anywhere along the chord - not only right next to a planet -
            # lands on an actual selectable data point.
            rs, thetas = chord_points(R_ASPECT, asp.p1_abs_pos, R_ASPECT, asp.p2_abs_pos, n=9)
            cd = [["aspect", key]] * len(rs)
            fig.add_trace(
                go.Scatterpolar(
                    r=rs,
                    theta=thetas,
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0)", width=18),
                    customdata=cd,
                    hovertext=hover_text,
                    hoverinfo="text",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatterpolar(
                    r=rs,
                    theta=thetas,
                    mode="lines",
                    line=dict(color=style["color"], width=width, dash=style["dash"]),
                    opacity=opacity,
                    customdata=cd,
                    hovertext=hover_text,
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    # --- planets & points -----------------------------------------------------
    if active_points:
        placed = []
        for name in active_points:
            p = point_data(subject, name)
            deg = p.abs_pos
            radius = R_PLANET_BASE
            for other_deg, _ in placed:
                if abs(wrap_delta(other_deg, deg)) < 6:
                    radius += R_PLANET_STEP
            placed.append((deg, radius))

            active = (
                sel_kind == "planet"
                and sel_key == name
                or sel_kind == "aspect"
                and name in highlighted_points
                or sel_kind == "sign"
                and p.sign_num == sel_key
            )
            if selection is None:
                opacity = 1.0
            elif active:
                opacity = 1.0
            else:
                opacity = 0.25

            retro = " ℞" if getattr(p, "retrograde", False) else ""
            hover = (
                f"<b>{point_label(name)}{retro}</b><br>"
                f"{point_position_str(p)}<br>"
                f"{point_house_str(p)}<br>"
                f"Speed: {p.speed:.3f}°/day"
            )
            # Invisible oversized marker underneath, purely to give the
            # planet a more forgiving click target than its visible glyph.
            fig.add_trace(
                go.Scatterpolar(
                    r=[radius],
                    theta=[deg],
                    mode="markers",
                    marker=dict(size=44, color="rgba(0,0,0,0)"),
                    customdata=[["planet", name]],
                    hovertext=[hover],
                    hoverinfo="text",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatterpolar(
                    r=[radius],
                    theta=[deg],
                    mode="markers+text",
                    marker=dict(
                        size=26 if active and selection else 22,
                        color=PAPER_BG,
                        line=dict(color=GOLD, width=2.5 if active and selection else 1.5),
                    ),
                    text=[PLANET_GLYPHS.get(name, name[:2])],
                    textfont=dict(size=15, color=GOLD),
                    opacity=opacity,
                    customdata=[["planet", name]],
                    hovertext=[hover],
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    # --- angles (ASC / MC) ------------------------------------------------------
    for label, point in (("ASC", subject.ascendant), ("MC", subject.medium_coeli)):
        fig.add_trace(
            go.Scatterpolar(
                r=[0, R_ANGLE_LINE],
                theta=[point.abs_pos, point.abs_pos],
                mode="lines",
                line=dict(color=GOLD, width=1.5, dash="dash"),
                opacity=0.8,
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[R_ANGLE_LABEL],
                theta=[point.abs_pos],
                mode="text",
                text=[label],
                textfont=dict(size=12, color=GOLD),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.update_layout(
        template=None,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR),
        uirevision="keep-zoom",
        polar=dict(
            bgcolor=CHART_BG,
            radialaxis=dict(visible=False, range=[0, RADIAL_MAX]),
            angularaxis=dict(visible=False, rotation=rotation, direction="counterclockwise"),
        ),
        showlegend=False,
        margin=dict(l=25, r=25, t=25, b=25),
        height=640,
        width=640,
    )
    return fig
