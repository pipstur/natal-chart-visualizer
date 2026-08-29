CLASSIC_PLANETS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]
OPTIONAL_POINTS = ["True_North_Lunar_Node", "True_South_Lunar_Node", "Mean_Lilith", "Chiron"]
ALL_POSSIBLE_POINTS = CLASSIC_PLANETS + OPTIONAL_POINTS
DEFAULT_ACTIVE_POINTS = CLASSIC_PLANETS + ["True_North_Lunar_Node", "Chiron"]

ASPECT_STYLE = {
    "conjunction": dict(color="#8a8278", dash="solid"),
    "opposition": dict(color="#c0392b", dash="solid"),
    "square": dict(color="#c0392b", dash="dot"),
    "trine": dict(color="#2b7fc0", dash="solid"),
    "sextile": dict(color="#2b9c6b", dash="dot"),
}
ASPECT_SYMBOLS = {
    "conjunction": "☌",
    "opposition": "☍",
    "square": "□",
    "trine": "△",
    "sextile": "⚹",
}

SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
SIGN_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
PLANET_GLYPHS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "True_North_Lunar_Node": "☊",
    "True_South_Lunar_Node": "☋",
    "Mean_Lilith": "⚸",
    "Chiron": "⚷",
}
HOUSE_ORDINAL_WORDS = [
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
    "Eleventh",
    "Twelfth",
]
HOUSE_NAME_TO_NUM = {f"{w}_House": i + 1 for i, w in enumerate(HOUSE_ORDINAL_WORDS)}

CHART_BG = "#0f1216"
PAPER_BG = "#15181e"
GRID_COLOR = "#2a2f3a"
TEXT_COLOR = "#e8e6e1"
GOLD = "#d9b877"
DIM_OPACITY = 0.15

# radial layout (all values are fractions of the polar radial range)
R_ASPECT = 0.52
R_PLANET_BASE = 0.60
R_PLANET_STEP = 0.045
R_HOUSE_BG_OUTER = 0.78
R_HOUSE_NUM = 0.14
R_SIGN_BASE = 0.80
R_SIGN_TOP = 0.965
R_SIGN_LABEL = 0.885
R_ANGLE_LINE = 1.0
R_ANGLE_LABEL = 1.03
RADIAL_MAX = 1.09
