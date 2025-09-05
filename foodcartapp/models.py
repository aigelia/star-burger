from collections import defaultdict

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.filter(menu_items__availability=True).distinct()


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):
    def available_for_order(self):
        restaurants = Restaurant.objects.prefetch_related('menu_items__product')
        restaurant_menu = defaultdict(set)

        for restaurant in restaurants:
            for item in restaurant.menu_items.all():
                restaurant_menu[restaurant].add(item.product)

        for order in self:
            products = set(item.product for item in order.items.all())
            available_restaurants = []

            for restaurant, menu_products in restaurant_menu.items():
                if products.issubset(menu_products):
                    available_restaurants.append(restaurant)

            order.available_restaurants = available_restaurants

        return self


class Order(models.Model):
    STATUS_CHOICES = [
        ('waiting_for_acceptation', 'Ожидает подтверждения'),
        ('sent_to_restaurant', 'Передан в ресторан'),
        ('given_to_courier', 'Передан курьеру'),
        ('completed', 'завершен'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('electronic', 'Электронно'),
        ('unknown', 'Не указан')
    ]
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='waiting_for_acceptation',
        verbose_name='статус заказа'
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_CHOICES,
        default='unknown',
        verbose_name='способ оплаты'
    )
    firstname = models.CharField(max_length=100, verbose_name='Имя')
    lastname = models.CharField(max_length=100, verbose_name='Фамилия', db_index=True)
    phonenumber = PhoneNumberField(verbose_name='Мобильный телефон', db_index=True)
    address = models.TextField(verbose_name='Адрес доставки')
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    cooking_by = models.ForeignKey(
        Restaurant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Ресторан, готовящий заказ"
    )
    registrated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время заказа'
    )
    called_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата и время звонка'
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата и время доставки'
    )

    def available_restaurants_display(self):
        restaurants = getattr(self, 'available_restaurants', [])
        return ", ".join([r.name for r in restaurants])

    available_restaurants_display.short_description = "Доступные рестораны"

    def total_price(self):
        result = self.items.aggregate(
            total=Sum(F('final_price') * F('quantity'), output_field=DecimalField())
        )['total']
        return result or 0

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        indexes = [
            models.Index(
                fields=[
                    'status',
                    'registrated_at',
                    'called_at',
                    'delivered_at',
                    'payment_method'
                ]
            ),
        ]

    def __str__(self):
        return f'Заказ клиента {self.firstname} {self.lastname}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='продукт'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='количество')
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='стоимость продукта'
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
        unique_together = [['order', 'product']]
        indexes = [
            models.Index(fields=['order', 'product']),
        ]

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'
