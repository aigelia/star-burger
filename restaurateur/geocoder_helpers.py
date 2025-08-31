from geopy.distance import geodesic
import requests
from environs import env

def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": env.str('YANDEX_API_GEOCODER'),
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def count_distance_to_restaurant(order_address, restaurant_address):
    order_coords = fetch_coordinates(order_address)
    restaurant_coords = fetch_coordinates(restaurant_address)

    if not order_coords or not restaurant_coords:
        return None

    distance_km = geodesic(order_coords, restaurant_coords).km
    return distance_km
