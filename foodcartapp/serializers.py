from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField, IntegerField

from foodcartapp.models import Product


class ProductInOrderSerializer(Serializer):
    product = PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = IntegerField(min_value=1)


class OrderSerializer(Serializer):
    firstname = CharField(error_messages={'required': 'Обязательное поле'})
    lastname = CharField(error_messages={'required': 'Обязательное поле'})
    phonenumber = PhoneNumberField(error_messages={'required': 'Обязательное поле'})
    address = CharField(error_messages={'required': 'Обязательное поле'})
    products = ProductInOrderSerializer(
        many=True,
        allow_empty=False,
        error_messages={'empty': 'Список продуктов не может быть пустым'}
    )
