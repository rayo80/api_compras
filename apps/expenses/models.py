from django.db import models

# Create your models here.
from apps.base.models import BaseModel
from apps.purchases.models import Purchase, Item
from apps.sales.models import CajaChica


class PaymentOrder(BaseModel):
    """Model definition for BaseModel."""


    MONEDA = (
        ('PEN', 'Soles'),
        ('USD', 'Dolares'),
    )

    aprobada = models.BooleanField(default=False)
    caja_id = models.ForeignKey(CajaChica, null=True)
    compra_id = models.ForeignKey(Purchase,)
    # la orden de pago que viene de caja chica generara una nueva compra "pago" con un unico
    # item asociado a un producto que sera nuestro concepto de egreso
    pagos = models.OneToOneField(Purchase, on_delete=models.CASCADE)  # jala el total de la compra
    moneda = models.CharField('moneda', max_length=20, choices=MONEDA, default='PEN')
    detalle = models.TextField(null=True, default=None, blank=True)
    total = models.IntegerField('total', default=0, blank=False, null=False)  # /100 to repr

    class Meta:
        abstract = True
        verbose_name = 'PaymentOrder'
        verbose_name_plural = 'PaymentOrders'


class Transaction(BaseModel):
    """Una transaccion deberia tener el monto total fijo
    es decir estaria asociada con la operacion total"""
    MONEDA = (
        ('PEN', 'Soles'),
        ('USD', 'Dolares'),
    )

    moneda = models.CharField('moneda', max_length=20, choices=MONEDA, default='PEN')
    observacion = models.TextField(null=True, default=None, blank=True)
    abono = models.IntegerField('total', default=0, blank=False, null=False)  # /100 to repr
    payment_order = models.OneToOneField(Item, on_delete=models.CASCADE, null=True)
    # caja_central
    class Meta:
        """Meta definition for BaseModel."""
        abstract = True
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
