from django.db import models

from apps.base.models import BaseModel


class MeasureUnit(BaseModel):
    """Model definition for MeasureUnit."""

    description = models.CharField('Descripcion', max_length=50, blank=False, null=False, unique=True)

    class Meta:
        """Meta definition for MeasureUnit."""

        verbose_name = 'MeasureUnit'
        verbose_name_plural = 'MeasureUnits'

    def __str__(self):
        """Unicode representation of MeasureUnit."""
        return self.description


# Create your models here.
class Product(BaseModel):
    """Model definition for Product."""

    name = models.CharField('Nombre de Producto', max_length=150, unique=True, blank=False, null=False)
    description = models.TextField('Descripcion', blank=True, null=False)
    stock = models.IntegerField(null=False, default=0)
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, null=True)
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.CASCADE,
                                     verbose_name="Unidad de medida", null=True, blank=True)

    class Meta:
        """Meta definition for Product."""

        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        """Unicode representation of Product."""
        return f'{self.name}: {self.stock}'
