from faker import Faker
from apps.purchases.models import Supplier

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

