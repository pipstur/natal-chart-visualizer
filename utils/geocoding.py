import streamlit as st
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


@st.cache_resource
def get_geolocator():
    return Nominatim(user_agent="natal-chart-explorer-app")


@st.cache_resource
def get_tz_finder():
    return TimezoneFinder()


def do_geocode():
    query = st.session_state.get("city_query", "").strip()
    if not query:
        st.session_state.geocode_error = "Type a city first."
        st.session_state.resolved_place = None
        return
    try:
        location = get_geolocator().geocode(query, timeout=10)
        if location is None:
            st.session_state.geocode_error = f"Couldn't find \u201c{query}\u201d."
            st.session_state.resolved_place = None
            return
        tz = get_tz_finder().timezone_at(lat=location.latitude, lng=location.longitude)
        st.session_state.lat_val = round(location.latitude, 4)
        st.session_state.lng_val = round(location.longitude, 4)
        if tz:
            st.session_state.tz_val = tz
        st.session_state.resolved_place = location.address
        st.session_state.geocode_error = None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.session_state.geocode_error = f"Geocoding service unreachable: {e}"
        st.session_state.resolved_place = None
    except Exception as e:
        st.session_state.geocode_error = f"Lookup failed: {e}"
        st.session_state.resolved_place = None
