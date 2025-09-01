from django.db import transaction
from django.http import JsonResponse
from django.template.defaulttags import comment
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from geolocations.services import fetch_coordinates, count_distance_to_restaurant
from .models import Product, Order, OrderProduct, OrderLocation, Location, Restaurant
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )

    products_fields = serializer.validated_data['products']
    products_objects = [
        OrderProduct(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            final_price=item['product'].price,
        )
        for item in products_fields
    ]
    OrderProduct.objects.bulk_create(products_objects)

    client_coords = fetch_coordinates(order.address)
    point_b = Location.objects.create(
        lat=client_coords[0] if client_coords else None,
        lng=client_coords[1] if client_coords else None,
        address=order.address
    )

    available_restaurants = Restaurant.objects.available_for_order(order)

    order_locations = []
    for restaurant in available_restaurants:
        restaurant_coords = fetch_coordinates(restaurant.address)
        point_a = Location.objects.create(
            lat=restaurant_coords[0] if restaurant_coords else None,
            lng=restaurant_coords[1] if restaurant_coords else None,
            address=restaurant.address
        )

        distance = None
        if client_coords and restaurant_coords:
            distance = count_distance_to_restaurant(order.address, restaurant.address)

        order_locations.append(
            OrderLocation(
                order=order,
                point_a=point_a,
                point_b=point_b,
                distance_km=distance,
                restaurant=restaurant
            )
        )

    OrderLocation.objects.bulk_create(order_locations)

    order_serializer = OrderSerializer(order)
    return Response(order_serializer.data)
