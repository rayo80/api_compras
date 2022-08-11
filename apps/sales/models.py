from django.db import models


# Create your models here.
class CajaChica(models.Model):
    """Model definition for Item."""

    id = models.AutoField(primary_key=True)
    recaudo = models.IntegerField()

    class Meta:
        """Meta definition for Item."""

        verbose_name = 'CajaChica'
        verbose_name_plural = 'CajasChica'
