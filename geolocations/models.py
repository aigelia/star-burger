from django.db import models


class Location(models.Model):
    lng = models.DecimalField('Долгота', max_digits=9, decimal_places=6)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    address = models.CharField('Адрес', max_length=255, blank=True)

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'
        indexes = [
            models.Index(fields=['lat', 'lng'])
        ]
        db_table = 'foodcartapp_location'

    def __str__(self):
        return self.address or f"{self.lat}, {self.lng}"

