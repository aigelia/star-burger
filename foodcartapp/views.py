import json

from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static

from .models import Product, Order, OrderProduct


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


def register_order(request):
    raw_order = json.loads(request.body.decode())
    order = Order.objects.create(
        firstname=raw_order.get('firstname'),
        lastname=raw_order.get('lastname'),
        phonenumber=raw_order.get('phonenumber'),
        address=raw_order.get('address')
    )
    raw_products = raw_order.get('products')
    for item in raw_products:
        product_obj = get_object_or_404(Product, id=item['product'])
        OrderProduct.objects.create(
            order=order,
            product=product_obj,
            quantity=item['quantity']
        )
    return JsonResponse({'success': True})
