# from apps.purchases.tests.purchases_factories import SupplierFactory
from rest_framework.test import APITestCase
from apps.purchases.models import Supplier


class SupplierFactory:

    def build_supplier_json(self):
        return {
            "tipo_documento": '1',
            "num_documento": '15256698',
            "legal_name": "Jhon Doe",
            "address": "48764 Howard Forge Apt. 421\nVanessaside, PA 19763",
            "phone": "996666363",
            "email": "elenasheremetev@skillion.org",
        }


class SupplierTestCase(APITestCase):

    def test_create_supplier(self):
        supplier_data = SupplierFactory().build_supplier_json()
        response = self.client.post('/purchases/supplier/',
                                    supplier_data,
                                    format='json')

        self.assertEqual(response.status_code, 201)

    def test_create_supplier_error(self):
        data = {
            "tipo_documento": None,
            "num_documento": "",
            "name": "",
            "address": "",
            "phone": "",
            "email": "",
            "cod_proveedor": "",
            "type_person": None
        }
        response = self.client.post('/purchases/supplier/',
                                    data, format='json')

        self.assertEqual(response.status_code, 400)
