from apps.products.models import Product
from apps.purchases.models import Supplier, Purchase
from apps.purchases.tests.purchases_factories import (PurchaseFactory)
from ddf import G
from rest_framework.test import APITestCase


class PurchaseTestCase(APITestCase):

    def setUp(self):
        G(Supplier)
        G(Product)
        G(Product)

    def test_create_purchase(self):
        purchase_data = PurchaseFactory().build_purchase_JSON()
        response = self.client.post('/purchases/purchase/',
                                    purchase_data,
                                    format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_purchase(self):
        G(Purchase, id=1)
        purchase_data = PurchaseFactory().build_purchase_JSON()
        purchase_data['items'][0]['cantidad'] = 100
        response = self.client.put('/purchases/purchase/1/',
                                   purchase_data,
                                   format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['items'][0]['cantidad'], 100)


"""
    def test_create_purchase_products_error(self):

        purchase_data = PurchaseFactory().build_purchase_JSON()
        response = self.client.post('/purchases/purchase/',
                                    purchase_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['items'][0]['producto'][0]),
                         'Invalid pk "1" - object does not exist.')
"""
