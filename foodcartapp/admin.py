from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from geolocations.services import fetch_coordinates, count_distance_to_restaurant
from .models import Product, Order, OrderProduct, OrderLocation
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from geolocations.models import Location


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    autocomplete_fields = ['product']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline]
    list_display = [
        'id',
        'firstname',
        'lastname',
        'phonenumber',
        'cooking_by',
        'available_restaurants_display',
    ]
    readonly_fields = ['available_restaurants_display']
    search_fields = ['firstname', 'lastname', 'phonenumber']
    fields = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'status',
        'available_restaurants_display',
        'cooking_by',
        'comment',
        'registrated_at',
        'called_at',
        'delivered_at',
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        client_coords = fetch_coordinates(obj.address)
        point_b = Location.objects.create(
            lat=client_coords[0] if client_coords else None,
            lng=client_coords[1] if client_coords else None,
            address=obj.address
        )
        OrderLocation.objects.filter(order=obj).delete()

        order_locations = []
        available_restaurants = Restaurant.objects.available_for_order(obj)
        for restaurant in available_restaurants:
            restaurant_coords = fetch_coordinates(restaurant.address)
            point_a = Location.objects.create(
                lat=restaurant_coords[0] if restaurant_coords else None,
                lng=restaurant_coords[1] if restaurant_coords else None,
                address=restaurant.address
            )

            distance = None
            if client_coords and restaurant_coords:
                distance = count_distance_to_restaurant(obj.address, restaurant.address)

            order_locations.append(
                OrderLocation(
                    order=obj,
                    point_a=point_a,
                    point_b=point_b,
                    restaurant=restaurant,
                    distance_km=distance
                )
            )

        OrderLocation.objects.bulk_create(order_locations)

    def response_change(self, request, obj):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return super().response_change(request, obj)
