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
            "total": 66.85,
            "igv": 10.20,
            "items": [
                {
                    "producto": "1",
                    "cantidad": 17,
                    "total_item": 32.13
                },
                {
                    "producto": "2",
                    "cantidad": 18,
                    "total_item": 34.72
                }
            ]
        }


class PurchaseTestCase(APITestCase):

    def setUp(self):
        G(Supplier)
        G(Product)
        G(Product)
        self.purchase = G(Purchase, id=1, num_documento='F001-789', total=3450)

    def test_list_purchases_returns(self):
        response = self.client.get('/purchases/purchase/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_purchases1_returns(self):
        response = self.client.get('/purchases/purchase/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 34.50)

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
