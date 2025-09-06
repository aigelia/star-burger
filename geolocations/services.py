from functools import lru_cache

from django.conf import settings
from geopy.distance import geodesic
import requests

from geolocations.models import Location


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_GEOCODER_KEY,
        "format": "json",
    })

    if not response.ok:
        return None

    decoded_response = response.json()
    if "error" in decoded_response:
        return None

    found_places = decoded_response['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None

    try:
        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return float(lat), float(lon)
    except (KeyError, ValueError):
        return None


@lru_cache(maxsize=None)
def get_or_create_location(address):
    if not address:
        return None

    location, created = Location.objects.get_or_create(address=address)

    if created:
        coords = fetch_coordinates(address)
        if coords:
            location.lat, location.lng = coords
            location.save()

    return location


def get_distance_between_addresses(address1, address2):
    loc1 = get_or_create_location(address1)
    loc2 = get_or_create_location(address2)

    if not loc1 or not loc2:
        return None

    if loc1.lat is None or loc1.lng is None or loc2.lat is None or loc2.lng is None:
        return None

    coords1 = (float(loc1.lat), float(loc1.lng))
    coords2 = (float(loc2.lat), float(loc2.lng))

    return geodesic(coords1, coords2).km
