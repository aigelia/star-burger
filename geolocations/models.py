from django.db import models


class Location(models.Model):
    lng = models.DecimalField('Долгота', max_digits=9, decimal_places=6, null=True)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6, null=True)
    address = models.CharField('Адрес', max_length=255, blank=True, unique=True)

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'

    def __str__(self):
        return self.address or f"{self.lat}, {self.lng}"

