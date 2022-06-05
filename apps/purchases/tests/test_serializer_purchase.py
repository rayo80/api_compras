from apps.purchases.api.serializers.purchase_serializers import \
    PurchaseWriteSerializer, ItemPurchaseSerializer
from apps.purchases.models import Purchase, Supplier, Product, Item
from django.test import TestCase
from faker import Faker
from ddf import G
from rest_framework.serializers import ValidationError
faker = Faker()


class ItemPurchaseSerializerTest(TestCase):

    def setUp(self):
        purchase = G(Purchase, id=100)
        self.product = G(Product, stock=100)

        self.serializer_data = {
            "producto": self.product.id,
            "cantidad": 19,
            "incluye_igv": True,
            "igv": 3.6,
            "total_item": 32,
        }

        self.item_atributtes = {
            "producto": self.product,
            "cantidad": 19,
            "incluye_igv": True,
            "igv": 3.6,
            "total_item": 32,
            "compra": purchase
        }

        self.item_instance = Item.objects.create(**self.item_atributtes)

    def test_cantidad_not_zero(self):
        test_data = self.serializer_data
        test_data['cantidad'] = 0
        serializer = ItemPurchaseSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['cantidad'][0].code, 'cant_zero')

    def test_incluye_igv_is_not_none(self):
        test_data = self.serializer_data
        test_data['incluye_igv'] = None
        serializer = ItemPurchaseSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['incluye_igv'][0].code, 'null')

    # FALTA VERIFICACION DE IGV
    def test_create_incrementa_stock(self):
        actual_stock = self.product.stock
        test_data = self.item_atributtes
        test_data['cantidad'] = 5
        serializer = ItemPurchaseSerializer()
        instance = serializer.create(test_data)
        diferencia = self.product.stock-actual_stock
        self.assertEqual(diferencia, instance.cantidad)

    def test_update_reduce_stock(self):
        actual_stock = self.product.stock
        test_data = self.item_atributtes
        print("actual_stock")
        test_data['producto'] = G(Product)
        test_data['cantidad'] = 3
        serializer = ItemPurchaseSerializer()
        instance = serializer.update(self.item_instance, test_data)
        diferencia = self.product.stock-actual_stock
        self.assertEqual(diferencia, instance.cantidad)



    def test_aumenta_stock(self):
        pass

class PurchaseWriteSerializerTest(TestCase):

    def setUp(self):

        # Instancias necesarias para la creacion de nuestra compra
        supplier = G(Supplier)
        product1 = G(Product)
        product2 = G(Product)
        # Json valido
        self.serializer_data = {
            "proveedor": "1",
            "tipo_documento": "1",
            "num_documento": "F001-00004",
            "fecha_documento": "2022-04-01",
            "fecha_vencimiento": "2022-04-01",
            "moneda": "PEN",
            "total": 66,
            "items": [
                {
                    "producto": "1",
                    "cantidad": 19,
                    "incluye_igv": True,
                    "igv": 3.6,
                    "total_item": 32
                },
                {
                    "producto": "2",
                    "cantidad": 18,
                    "incluye_igv": True,
                    "igv": 2.5,
                    "total_item": 34
                }
            ]
        }

        # Data de prueba usada mas adelante
        self.purchase_attributes = {
            "id": 1,
            "proveedor": supplier,
            "tipo_documento": "1",
            "num_documento": "F001-00004",
            "fecha_documento": "2022-04-01",
            "fecha_vencimiento": "2022-04-01",
            "moneda": "PEN",
            "total": 66,
        }

        self.purchase_instance = Purchase.objects.create(**self.purchase_attributes)

        self.item1_attributes = {
            "producto": product1,
            "cantidad": 17,
            "incluye_igv": True,
            "igv": 3.6,
            "total_item": 32,
            "compra": self.purchase_instance
        }

        self.item2_attributes = {
            "producto": product2,
            "cantidad": 18,
            "incluye_igv": True,
            "igv": 2.5,
            "total_item": 34,
            "compra": self.purchase_instance
        }

        self.item1_instance = Item.objects.create(**self.item1_attributes)
        self.item2_instance = Item.objects.create(**self.item2_attributes)

    def test_no_exits_supplier(self):
        test_data = self.serializer_data
        test_data['proveedor'] = '500'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['proveedor'][0].code, 'does_not_exist')

    def test_no_exits_products(self):
        test_data = self.serializer_data
        test_data['items'][0]['producto'] = '300'
        test_data['items'][1]['producto'] = '400'
        serializer = PurchaseWriteSerializer(data=test_data)

        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)        
        self.assertEqual(serializer.errors['items'][0]['producto'][0].code,
                         'does_not_exist')
        self.assertEqual(er.exception.detail['items'][0]['producto'][0].code,
                         'does_not_exist')

    # validate_Items

    def test_validate_items_not_none(self):
        self.serializer_data['items'] = []
        serializer = PurchaseWriteSerializer(data=self.serializer_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['items'][0].code, 'no_items')

    # validate_total
    def test_validate_total_not_string(self):
        test_data = self.serializer_data
        test_data['total'] = 'sadasd'
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['total'][0].code, 2)

    def test_validate_total_is_not_none(self):
        test_data = self.serializer_data
        test_data['total'] = None
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['total'][0].code, 'null')

    def test_validate_total_is_not_blank(self):
        test_data = self.serializer_data
        test_data['total'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['total'][0].code, 'blank')

    def test_validate_total_is_dif_sum_items(self):
        test_data = self.serializer_data
        test_data['total'] = 43.54
        test_data['items'][0]['total_item'] = 21.30
        test_data['items'][1]['total_item'] = 22.25
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['total'][0].code, 'dif_sum')

    def test_validate_total_is_sum_items(self):
        test_data = self.serializer_data
        test_data['total'] = 43.55
        test_data['items'][0]['total_item'] = 21.30
        test_data['items'][1]['total_item'] = 22.25
        serializer = PurchaseWriteSerializer(data=test_data)
        self.assertEqual(serializer.is_valid(), True)

    # num_documento
    def test_validate_num_documento_is_not_blank(self):
        test_data = self.serializer_data
        test_data['num_documento'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['num_documento'][0].code, 'blank')

    def test_validate_num_documento_correct_format(self):
        test_data = self.serializer_data
        test_data['num_documento'] = 'FVR'
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['num_documento'][0].code, 'guion')

    def test_validate_num_documento_fields_correct_format(self):
        test_data = self.serializer_data
        test_data['num_documento'] = 'asd-asd'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'serie4')

        """
        # Caso para mas adelante
        test_data['num_documento'] = '2d56-asd'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'BorForE')
        """
        test_data['num_documento'] = 'F256-asd'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'corr_non_num')

    # fecha documento
    def test_validate_fecha_documento_is_invalid(self):
        test_data = self.serializer_data
        test_data['fecha_documento'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_documento'][0].code, 'invalid')

    def test_validate_fecha_documento_is_not_null(self):
        test_data = self.serializer_data
        test_data['fecha_documento'] = None
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_documento'][0].code, 'null')

    # fecha vencimiento
    def test_validate_fecha_vencimiento_is_invalid(self):
        test_data = self.serializer_data
        test_data['fecha_vencimiento'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_vencimiento'][0].code, 'invalid')

    def test_validate_fecha_vencimiento_is_not_null(self):
        test_data = self.serializer_data
        test_data['fecha_vencimiento'] = None
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_vencimiento'][0].code, 'null')

    def test_validate_fecha_vencimiento_is_not_less_than_fdom(self):
        test_data = self.serializer_data
        test_data['fecha_documento'] = '2022-04-02'
        test_data['fecha_vencimiento'] = '2022-04-01'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_vencimiento'][0].code, 
                         'fven<fdoc')

    def test_create_serializer(self):
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(data=test_data)
        serie, correlativo = test_data['num_documento'].split('-')
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(instance.serie, serie)
        self.assertEqual(instance.correlativo, correlativo)
        self.assertEqual(str(instance), 'Compra 1 F001-00004')
        self.assertEqual(instance.id, 2)
        self.assertEqual(instance.items.count(), 2)

    def test_update_serializer(self):
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(str(instance), 'Compra 1 F001-00004')
        self.assertEqual(instance.id, 1)

    def test_items_update_delete_previous(self):
        test_data = self.serializer_data
        # print(type(self.purchase_instance.items))
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertFalse(instance.items.all()[0].state)
        self.assertFalse(instance.items.all()[1].state)

    def test_previous_items_update_stock(self):
        test_data = self.serializer_data
        # print(type(self.purchase_instance.items))
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertFalse(instance.items.all()[0].state)
        self.assertFalse(instance.items.all()[1].state)


"""
    def test_update_serializer(self):
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        self.assertEqual(str(instance), 'Compra 1 F001-00004')
        self.assertEqual(instance.id, 1)
        self.assertEqual(instance.items.count(), 2)
    #  test create generate item

"""