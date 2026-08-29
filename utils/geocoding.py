import requests
import streamlit as st
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


@st.cache_resource
def get_geolocator():
    return Nominatim(user_agent="natal-chart-explorer-app v1.0 (vojislavstevanovic171@gmail.com)")


@st.cache_resource
def get_tz_finder():
    return TimezoneFinder()


@st.cache_data(ttl=86400)
def geocode_city(query):
    response = requests.get(
        "https://api.geoapify.com/v1/geocode/search",
        params={
            "text": query,
            "apiKey": st.secrets["GEOAPIFY_API_KEY"],
            "limit": 1,
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("features"):
        return None

    properties = data["features"][0]["properties"]

    return {
        "latitude": round(properties["lat"], 4),
        "longitude": round(properties["lon"], 4),
        "address": properties.get("formatted", query),
    }


def do_geocode():
    query = st.session_state.get("city_query", "").strip()

    if not query:
        st.session_state.geocode_error = "Type a city first."
        st.session_state.resolved_place = None
        return

    try:
        result = geocode_city(query)

        if result is None:
            st.session_state.geocode_error = f"Couldn't find “{query}”."
            st.session_state.resolved_place = None
            return

        tz = get_tz_finder().timezone_at(
            lat=result["latitude"],
            lng=result["longitude"],
        )
        st.session_state.lat_val = str(result["latitude"])
        st.session_state.lng_val = str(result["longitude"])
        st.session_state.tz_val = tz
        st.session_state.resolved_place = result["address"]
        st.session_state.geocode_error = None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.session_state.geocode_error = f"Geocoding service unreachable: {e}"
        st.session_state.resolved_place = None
    except Exception as e:
        st.session_state.geocode_error = f"Lookup failed: {e}"
        st.session_state.resolved_place = None
