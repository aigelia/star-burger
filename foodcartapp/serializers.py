from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer, DecimalField
from rest_framework.serializers import CharField, IntegerField

from foodcartapp.models import Product


class ProductInOrderSerializer(Serializer):
    product = PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = IntegerField(min_value=1)
    final_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

class OrderSerializer(Serializer):
    firstname = CharField(error_messages={'required': 'Обязательное поле'})
    lastname = CharField(error_messages={'required': 'Обязательное поле'})
    phonenumber = PhoneNumberField(error_messages={'required': 'Обязательное поле'})
    address = CharField(error_messages={'required': 'Обязательное поле'})
    products = ProductInOrderSerializer(
        many=True,
        write_only=True,
        allow_empty=False,
        error_messages={'empty': 'Список продуктов не может быть пустым'}
    )
