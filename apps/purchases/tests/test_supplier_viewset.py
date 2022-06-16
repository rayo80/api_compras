# from apps.purchases.tests.purchases_factories import SupplierFactory
from rest_framework.test import APITestCase
from apps.purchases.models import Supplier
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
