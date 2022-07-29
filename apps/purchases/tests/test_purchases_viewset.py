from apps.products.models import Product
from apps.purchases.models import Supplier, Purchase
# from apps.purchases.tests.purchases_factories import (PurchaseFactory)
from ddf import G
from rest_framework.test import APITestCase


class PurchaseFactory:

    def build_purchase_json(self):
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


class PurchaseTestCase(APITestCase):

    def setUp(self):
        G(Supplier)
        G(Product)
        G(Product)
        self.purchase = G(Purchase, id=1, num_documento='F001-789')

    def test_create_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_json()
        response = self.client.post('/purchases/purchase/',
                                    purchase_data,
                                    format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['items'][0]['cantidad'], 17)

    def test_create_purchase_products_error(self):
        purchase_data = PurchaseFactory().build_purchase_json()
        purchase_data['items'][0]['producto'] = '50'
        response = self.client.post('/purchases/purchase/',
                                    purchase_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['items'][0]['producto'][0].code, 'does_not_exist')

    def test_update_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_json()
        purchase_data['num_documento'] = 'F001-00005'
        purchase_data['items'][0]['cantidad'] = 100
        response = self.client.put('/purchases/purchase/1/',
                                   purchase_data,
                                   format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['num_documento'], 'F001-00005')
        self.assertEqual(response.data['items'][0]['cantidad'], 100)

    def test_delete_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_json()
        response = self.client.delete('/purchases/purchase/1/',
                                      purchase_data,
                                      format='json')
        self.assertEqual(response.status_code, 204)
