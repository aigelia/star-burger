import requests

from django.conf import settings
from geopy.distance import geodesic


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


def count_distance_to_restaurant(order_address, restaurant_address):
    order_coords = fetch_coordinates(order_address)
    restaurant_coords = fetch_coordinates(restaurant_address)

    if not order_coords or not restaurant_coords:
        return None

    distance_km = geodesic(order_coords, restaurant_coords).km
    return distance_km
