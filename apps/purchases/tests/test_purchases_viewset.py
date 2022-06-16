from apps.products.models import Product
from apps.purchases.models import Supplier, Purchase
# from apps.purchases.tests.purchases_factories import (PurchaseFactory)
from ddf import G
from rest_framework.test import APITestCase
from faker import Faker
faker = Faker()

class SupplierFactory:

    def build_supplier_JSON(self):
        return {
            "tipo_documento": '1',
            "num_documento": '15256698',
            "name": faker.name(),
            "address": faker.address(),
            "phone": "996666363",
            "email": faker.email(),
        }

    def create_supplier(self):
        return Supplier.objects.create(**self.build_supplier_JSON())

class PurchaseFactory:

    def build_purchase_JSON(self):
        return {
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
                    "cantidad": 17,
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

class PurchaseTestCase(APITestCase):

    def setUp(self):
        G(Supplier)
        G(Product)
        G(Product)
        self.purchase = G(Purchase, id=1, num_documento='F001-789')

    def test_create_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_JSON()
        response = self.client.post('/purchases/purchase/',
                                    purchase_data,
                                    format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['items'][0]['cantidad'], 17)

    def test_create_purchase_products_error(self):
        purchase_data = PurchaseFactory().build_purchase_JSON()
        purchase_data['items'][0]['producto'] = '50'
        response = self.client.post('/purchases/purchase/',
                                    purchase_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['items'][0]['producto'][0].code, 'does_not_exist')

    def test_update_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_JSON()
        purchase_data['num_documento'] = 'F001-00005'
        purchase_data['items'][0]['cantidad'] = 100
        response = self.client.put('/purchases/purchase/1/',
                                   purchase_data,
                                   format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['num_documento'], 'F001-00005')
        self.assertEqual(response.data['items'][0]['cantidad'], 100)

    def test_delete_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_JSON()
        response = self.client.delete('/purchases/purchase/1/',
                                      purchase_data,
                                      format='json')
        self.assertEqual(response.status_code, 204)
