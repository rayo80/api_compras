from apps.purchases.tests.purchases_factories import SupplierFactory
from rest_framework.test import APITestCase
class SupplierTestCase(APITestCase):

    def test_create_supplier(self):
        supplier_data = SupplierFactory().build_supplier_JSON()
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
