from django.db import models

# Create your models here.
from apps.base.models import BaseModel
from apps.purchases.models import Purchase, Item
from apps.sales.models import CajaChica


class PaymentOrder(BaseModel):
    """Model definition for BaseModel."""

    DOCUMENTO = (
        ('1', '01-FACTURA'),
        ('3', '03-BOLETA'),
        ('x', 'RECIBO POR HONORARIOS')
        ('x', 'CONSTANCIA DE DEPOSITO')
        ('x', 'RECIBOS POR SERVICIO')
    )

    MONEDA = (
        ('PEN', 'Soles'),
        ('USD', 'Dolares'),
    )

    tipo_documento = models.CharField('tipo de documento', max_length=20, choices=DOCUMENTO)
    num_documento = models.CharField('numero de documento', max_length=13, help_text='numero')

    aprobada = models.BooleanField(default=False)
    caja_id = models.ForeignKey(CajaChica, null=True)
    # la orden de pago que viene de caja chica generara una nueva compra "pago" con un unico
    # item asociado a un producto que sera nuestro concepto de egreso
    pagos = models.OneToOneField(Purchase, on_delete=models.CASCADE)  # jala el total de la compra
    fecha_documento = models.DateField('fecha de emision del comprobante', auto_now=False, auto_now_add=False)
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

    class Meta:
        """Meta definition for BaseModel."""
        abstract = True
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
