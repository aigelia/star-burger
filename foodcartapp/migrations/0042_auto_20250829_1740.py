from django.db import migrations


def fill_final_price(apps, schema_editor):
    OrderProduct = apps.get_model('foodcartapp', 'OrderProduct')
    Product = apps.get_model('foodcartapp', 'Product')

    items_to_update = OrderProduct.objects.filter(final_price__isnull=True).iterator()

    updated_items = []
    for item in items_to_update:
        item.final_price = item.product.price
        updated_items.append(item)

    OrderProduct.objects.bulk_update(updated_items, ['final_price'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_orderproduct_final_price'),
    ]

    operations = [
        migrations.RunPython(fill_final_price),
    ]
