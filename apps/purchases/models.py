from django.db import models
from apps.base.models import BaseModel
from apps.products.models import Product
# from django.db.models.signals import post_save, post_delete


class Supplier(BaseModel):
    DOCUMENT = (
        ('6', 'RUC'),
        ('1', 'DNI'),
    )
    TYPE_PERSON = (
        (None, 'SIN ESPECIFICAR'),
        ('j', 'JURIDICA'),
        ('n', 'NATURAL'),
    )

    tipo_documento = models.CharField('tipo de documento', max_length=20, choices=DOCUMENT, default='RUC')
    num_documento = models.CharField(unique=True, max_length=11, blank=False, null=False)
    legal_name = models.CharField('Razón Social', unique=True, max_length=150, null=False, blank=False)
    address = models.CharField('Direccion', max_length=200, null=True, blank=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    cod_proveedor = models.CharField(max_length=50, blank=True, null=True, default=None)
    type_person = models.CharField('Tipo de persona', max_length=4, choices=TYPE_PERSON,
                                   null=True, default='SIN ESPECIFICAR')

    class Meta:
        ordering = ['id']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.legal_name

    def to_dict(self):
        return {
            'id': self.id,
            'ruc': self.num_documento,
            'name': self.legal_name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }


class Purchase(BaseModel):
    """Model definition for Purchase."""
    COMPROBANTE = (
        ('0', 'INTERNO'),
        ('1', '01-FACTURA'),
        ('3', '03-BOLETA'),
        ('2', 'RECIBO POR HONORARIOS'),
        ('13', 'CONSTANCIA DE DEPOSITO'),
        ('14', 'RECIBOS POR SERVICIO')
    )

    MONEDA = (
        ('PEN', 'Soles'),
        ('USD', 'Dolares'),
    )

    proveedor = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True)
    tipo_documento = models.CharField('tipo de documento', max_length=20, choices=COMPROBANTE)
    num_documento = models.CharField('numero de documento', max_length=13, help_text='factura/boleta')
    serie = models.CharField('serie', max_length=4)
    correlativo = models.CharField('correlativo', max_length=8)
    fecha_documento = models.DateField('fecha de emision del comprobante', auto_now=False, auto_now_add=False)
    fecha_vencimiento = models.DateField('fecha de vencimiento del comprobante', auto_now=False, auto_now_add=False)
    moneda = models.CharField('moneda', max_length=20, choices=MONEDA, default='PEN')
    observacion = models.TextField(null=True, default=None, blank=True)
    total = models.IntegerField('total', default=0, blank=False, null=False)  # /100 to repr
    igv = models.IntegerField('igv', default=0, blank=False, null=False)  # /100 to repr
    abonado = models.IntegerField('total', default=0, blank=False, null=False)  # /100 to repr
    pagada = models.BooleanField('pago completado', default=True, null=False)

    class Meta:
        """Meta definition for Purchase."""

        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        """Unicode representation of Compra."""
        return f'Compra {self.id} {self.num_documento}'


class Item(models.Model):
    """Model definition for Item."""

    id = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    total_item = models.IntegerField(blank=False, null=True)  # /100 to representate
    producto = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, default=None)
    compra = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')

    class Meta:
        """Meta definition for Item."""

        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        """Unicode representation of Item."""
        return f'item {self.id} en {self.compra}'

    # LOGIC BUSSINES #
    def increment_stock(self, *args, **kwargs):
        # este refresh actualiza el valor actual del stock
        self.producto.stock += self.cantidad
        self.producto.save()
        return self.producto.stock

    def decrement_stock(self, *args, **kwargs):
        self.producto.stock -= self.cantidad
        self.producto.save()
        return self.producto.stock


    """
    
    # Opcion por signals
    def aument_product(sender, instance, **kwargs):
        item = instance.id
        purchase = instance.compra
        if purchase.state:  # la compra existe
            print(item)
            print("aumento")

    def reduce_product(sender, instance, **kwargs):
        item = instance.id
        purchase = instance.compra
        if purchase:
            print(item)
            print("decremento")


    post_save.connect(aument_product, sender=Item)
    post_delete.connect(reduce_product, sender=Item)
    """
