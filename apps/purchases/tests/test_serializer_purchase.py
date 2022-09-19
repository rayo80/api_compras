from apps.purchases.api.serializers.purchase_serializers import \
    PurchaseWriteSerializer, ItemPurchaseSerializer
from apps.purchases.models import Purchase, Supplier, Product, Item
from django.test import TestCase
from ddf import G
from rest_framework.serializers import ValidationError
from copy import deepcopy


class ItemPurchaseSerializerTest(TestCase):

    def setUp(self):
        self.purchase = G(Purchase, id=100, num_documento="F001-8888")
        self.product1 = G(Product, stock=100)
        self.product2 = G(Product, stock=20)
        self.product3 = G(Product, stock=0)
        self.product4 = G(Product, stock=80)

        self.serializer_data = {
            "producto": 1,
            "cantidad": 19,
            "total_item": 32,
        }

        self.item_atributtes = {
            "producto": self.product1,
            "cantidad": 29,
            "total_item": 33,
            "compra": self.purchase
        }

        atributtes1 = self.item_atributtes
        atributtes2 = self.item_atributtes.copy()
        atributtes2['cantidad'] = 35
        atributtes2['producto'] = self.product2
        atributtes3 = self.item_atributtes.copy()
        atributtes3['cantidad'] = 48
        atributtes3['producto'] = self.product4

        # generamos 3 instancias de items
        self.item_instance1 = Item.objects.create(**atributtes1)
        self.item_instance2 = Item.objects.create(**atributtes2)
        self.item_instance3 = Item.objects.create(**atributtes3)

        # Para probar la creacion y lka actualizacion necesito
        # jsons validados listos para ser creados
        self.list_instances = [self.item_instance1, self.item_instance2, self.item_instance3]

        # como los items nuevos y los items actuales no comparten la misma instancia
        # de producto hay que generar copias para el correcto testeo
        prod1_copy = deepcopy(self.product1)
        prod2_copy = deepcopy(self.product2)
        prod3_copy = deepcopy(self.product3)

        self.to_created_data = [
            {
                "producto": prod1_copy,
                "cantidad": 19,
                "total_item": 3200,
                "compra": self.purchase,
            },
            {
                "producto": prod2_copy,
                "cantidad": 25,
                "total_item": 26,
                "compra": self.purchase
            },
            {
                "producto": prod3_copy,
                "cantidad": 27,
                "total_item": 35,
                "compra": self.purchase
            }
        ]

    # VALIDACIONES
    def test_cantidad_not_zero(self):
        test_data = self.serializer_data
        test_data['cantidad'] = 0
        serializer = ItemPurchaseSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['cantidad'][0].code, 'cant_zero')

    def test_create_incrementa_stock(self):
        """Aca solo testeo que mi funcion create
        del serializer realice el incremento
        correctamente"""

        actual_stock = self.product1.stock
        # solo un valor de la lista de creación
        test_data = [self.to_created_data[0], ]
        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        instance = serializer.create(test_data)
        self.assertEqual(instance[0].producto.stock-actual_stock, instance[0].cantidad)

    # LOGICA EN CREACION
    def test_create_multiple_items_increment_stocks(self):
        actual_stock = self.product1.stock
        actual_stock2 = self.product2.stock
        test_data = self.to_created_data
        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        instance = serializer.create(test_data)
        # una vez se da create self.prod... aumentan
        self.assertEqual(instance[0].producto.stock-actual_stock, instance[0].cantidad)
        self.assertEqual(instance[1].producto.stock-actual_stock2, instance[1].cantidad)

    # UPDATE CASOS
    def test_generate_new_items_correctly(self):
        test_data = self.to_created_data  # varios items
        # lista instancias actuales e la compra
        lista_items = [self.item_instance1, self.item_instance2,
                       self.item_instance3]  # varios items

        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        instance = serializer.update(lista_items, test_data)

        # verificando la creacion de nuevos items con su cantidad
        self.assertEqual(instance[0].cantidad, 19)
        self.assertEqual(instance[1].cantidad, 25)
        self.assertEqual(instance[2].cantidad, 27)

    def test_update_reduce_stock_if_item_same_product(self):
        actual_stock = self.product1.stock  # 100
        # ingresamos una lista con un solo item
        test_data = [self.to_created_data[0]]  # cantidad = 19
        # lista instancias(items) 1 item con el mismo producto
        lista_items = [self.item_instance1]  # cantidad = 29
        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        instance = serializer.update(lista_items, test_data)
        # si entro un item con el mismo product que reduzca y luego aumente
        self.product1.refresh_from_db()
        diferencia = self.product1.stock-actual_stock

        self.assertEqual(diferencia, instance[0].cantidad-lista_items[0].cantidad)  # 19-29
        self.assertEqual(diferencia, -10)
        self.assertEqual(self.product1.stock, 90)

    def test_multiple_update_for_same_product(self):
        actual_stock1 = self.product1.stock  # stock:100
        actual_stock2 = self.product2.stock  # stock:20
        actual_stock3 = self.product3.stock  # stock:0
        actual_stock4 = self.product4.stock  # stock:80

        test_data = self.to_created_data  # varios items

        # lista instancias actuales e la compra
        lista_items = [self.item_instance1, self.item_instance2,
                       self.item_instance3]  # varios items

        # ingresan items de producto 1 ,2 y 3 y salen los de 1, 2 y 4
        variacion1 = test_data[0]['cantidad']-lista_items[0].cantidad  # 19-29
        variacion2 = test_data[1]['cantidad']-lista_items[1].cantidad  # 25-35
        variacion3 = test_data[2]['cantidad']  # 27
        variacion4 = -lista_items[2].cantidad  # -38

        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        instance_items = serializer.update(lista_items, test_data)

        self.product4.refresh_from_db()

        # verificando que el stock haya variado
        self.assertEqual(variacion1, instance_items[0].producto.stock-actual_stock1)  # -10
        self.assertEqual(variacion2, instance_items[1].producto.stock-actual_stock2)  # -10
        self.assertEqual(variacion3, instance_items[2].producto.stock-actual_stock3)  # 27
        self.assertEqual(variacion4, self.product4.stock-actual_stock4)  # -48

    # DELETE CASES
    def test_delete_items(self):
        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        # lista instancias actuales e la compra
        lista_items = [self.item_instance1, self.item_instance2,
                       self.item_instance3]
        serializer.delete(lista_items)
        self.assertFalse(Item.objects.filter(
                         pk=self.item_instance1.id).exists())
        self.assertFalse(Item.objects.filter(
                         pk=self.item_instance2.id).exists())
        self.assertFalse(Item.objects.filter(
                         pk=self.item_instance3.id).exists())

    def test_delete_reduce_stock(self):
        actual_stock1 = self.product1.stock  # stock:100
        actual_stock2 = self.product2.stock  # stock:20
        serializer = ItemPurchaseSerializer(read_only=False, many=True)
        # lista instancias actuales e la compra
        lista_items = [self.item_instance1, self.item_instance2,
                       self.item_instance3]  # 29,35,48(product4)
        serializer.delete(lista_items)
        print(self.product1.stock, self.product2.stock, self.product3.stock)
        self.assertEqual(-lista_items[0].cantidad, self.product1.stock-actual_stock1)  # -10
        self.assertEqual(-lista_items[1].cantidad, self.product2.stock-actual_stock2)  # -10
        self.assertEqual(self.product4.stock, 32)  # 80-48

    # TODO: TESTEAR CANTIDAD ES POSITIVAL


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
            "igv": 10.07,
            "items": [
                {
                    "producto": "1",
                    "cantidad": 19,
                    "igv": 4.88,
                    "total_item": 32
                },
                {
                    "producto": "2",
                    "cantidad": 18,
                    "igv": 5.19,
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
            "total": 65,
            "igv": 9.91,
        }

        self.purchase_instance = Purchase.objects.create(**self.purchase_attributes)

        self.item1_attributes = {
            "producto": product1,
            "cantidad": 17,
            "total_item": 32,
            "compra": self.purchase_instance
        }

        self.item2_attributes = {
            "producto": product2,
            "cantidad": 18,
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

    def test_items_dont_have_same_product(self):
        self.serializer_data['items'][0]['producto'] = '2'
        serializer = PurchaseWriteSerializer(data=self.serializer_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['items'][0].code,
                         'not_same_product')

    # validate igv
    def test_validate_igv_purchase(self):
        test_data = self.serializer_data
        test_data['igv'] = 21.60
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        print(er.exception.detail)
        self.assertEqual(er.exception.detail['igv'][0].code, 'dif_igv')

    # validate total
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
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['total'][0].code, 'invalid')

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
        test_data['total'] = 43.85
        test_data['igv'] = 6.69
        test_data['items'][0]['total_item'] = 21.60
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

    def test_not_validate_interno(self):
        test_data = self.serializer_data
        test_data['num_documento'] = '4559'
        test_data['tipo_documento'] = '0'
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())

    def test_validate_num_documento_correct_format(self):
        test_data = self.serializer_data
        test_data['num_documento'] = 'FVR'
        test_data['tipo_documento'] = '1'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'guion')

    def test_validate_serie_correct_format(self):
        test_data = self.serializer_data
        test_data['num_documento'] = 'asd-asd'
        test_data['tipo_documento'] = '1'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'serie4')

    def test_validate_num_document_correct_initial_lettter(self):
        # Caso para mas adelante
        test_data = self.serializer_data
        test_data['num_documento'] = 'D001-a0003'
        test_data['tipo_documento'] = '1'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'BorForE')

    def test_validate_correlativo_correct_format(self):
        """Validamos que sea numeral cuando sea factura"""
        test_data = self.serializer_data
        test_data['num_documento'] = 'F256-asd'
        test_data['tipo_documento'] = '1'
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code,
                         'corr_non_num')
        # {'non_field_errors': [ErrorDetail(string='El valor de correlativo no tiene numeros', code='corr_non_num')]}
        # {'num_documento': [ErrorDetail(string='El valor de correlativo no tiene numeros', code='corr_non_num')]}

    # fecha documento
    def test_validate_fecha_documento_is_invalid(self):
        test_data = self.serializer_data
        test_data['fecha_documento'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_documento'][0].code,
                         'invalid')

    def test_validate_fecha_documento_is_not_null(self):
        test_data = self.serializer_data
        test_data['fecha_documento'] = None
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_documento'][0].code,
                         'null')

    # FECHA VENCIMIENTO
    def test_validate_fecha_vencimiento_is_invalid(self):
        test_data = self.serializer_data
        test_data['fecha_vencimiento'] = ''
        serializer = PurchaseWriteSerializer(data=test_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['fecha_vencimiento'][0].code,
                         'invalid')

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

    def test_create_multiple_fields_serializer(self):
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(data=test_data)
        serie, correlativo = test_data['num_documento'].split('-')
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(instance.serie, serie)
        self.assertEqual(instance.correlativo, correlativo)
        self.assertEqual(Purchase.objects.filter(id=instance.id).count(), 1)
        self.assertEqual(instance.id, 2)
        self.assertEqual(instance.items.count(), 2)

    def test_create_single_items_serializer(self):
        test_data = self.serializer_data
        total = test_data["total"]
        test_data["items"] = [test_data["items"][0]]
        test_data["items"][0]["total_item"] = total
        serializer = PurchaseWriteSerializer(data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(instance.items.count(), 1)

    # UPDATE CASES
    def test_update_serializer(self):
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(str(instance), 'Compra 1 F001-00004')
        self.assertEqual(instance.id, 1)

    def test_update_purchase_delete_previous_items(self):
        """Los items que se tenian antes de la actualizacion se eliminan"""
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertFalse(instance.items.filter(pk=1).exists())
        self.assertFalse(instance.items.filter(pk=2).exists())

    def test_update_stock_correctly(self):
        """El stock se actualiza correctamente"""
        test_data = self.serializer_data
        serializer = PurchaseWriteSerializer(self.purchase_instance, data=test_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(instance.items.all()[0].producto.stock, 2)

    # DELETE PURCHASE
    def test_delete_purchase(self):
        purchase = self.purchase_instance
        print(purchase.state)
        serializer = PurchaseWriteSerializer(data={'motivo': "Eliminado por el bien de todos"})
        serializer.destroy(purchase)
        print(serializer.initial_data)
        # self.assertFalse(Purchase.objects.filter(id=1).exists())
        self.assertFalse(purchase.state)
        self.assertEqual(purchase.items.count(), 0)
