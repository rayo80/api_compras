from faker import Faker
from django.test import TestCase
from apps.purchases.models import Supplier
from apps.purchases.api.serializers.supplier_serializers import SupplierSerializer

faker = Faker()

class SupplierSerilizerTest(TestCase):

    def setUp(self):
        # datos ingresados
        self.supplier_attributes = {
            "tipo_documento": '1',
            "num_documento": '15256698',
            "name": faker.name(),
            "address": faker.address(),
            "phone": "996666363",
            "email": faker.email(),
        }

        self.supplier = Supplier.objects.create(**self.supplier_attributes)
        self.serializer = SupplierSerializer(instance=self.supplier)

        # Data de prueba usada mas adelante
        self.serializer_data = {
            "tipo_documento": '1',
            "num_documento": '15256699',
            "name": faker.name(),
            "address": faker.address(),
            "phone": "996666363",
            "email": faker.email(),
        }

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()),
                         set(['tipo_documento', 'num_documento', 'name',
                              'address', 'phone', 'email', 'cod_proveedor', 
                              'type_person', 'id']))

    def test_tipo_documento_field_contained(self):
        data = self.serializer.data
        self.assertEqual(data['tipo_documento'],
                         self.supplier_attributes['tipo_documento'])

    def test_validate_num_documento_is_numeric(self):
        self.serializer_data['num_documento'] = 'valormalo'
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors['num_documento'][0]),
                         'El valor contiene caracteres no numericos')
        self.assertEqual(serializer.errors['num_documento'][0].code, 0)

    def test_validate_num_documento_with_tipo_6(self):
        self.serializer_data['tipo_documento'] = '6'
        self.serializer_data['num_documento'] = '415263'
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['num_documento'][0].code, 1)

    def test_validate_num_documento_with_tipo_1(self):
        self.serializer_data['tipo_documento'] = '1'
        self.serializer_data['num_documento'] = '415263'
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['num_documento'][0].code, 2)

    def test_name_is_not_none(self):
        self.serializer_data['name'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['name'][0]), 'This field may not be null')

    def test_name_is_not_blank(self):
        self.serializer_data['name'] = ''
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['name'][0]), 'This field may not be blank')

    def test_num_is_not_none(self):
        self.serializer_data['num_documento'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['num_documento'][0]), 'This field may not be null')

    def test_num_is_not_blank(self):
        self.serializer_data['num_documento'] = ''
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['num_documento'][0]), 'This field may not be blank')

    def test_tipo_is_not_none(self):
        self.serializer_data['tipo_documento'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['tipo_documento'][0]), 'This field may not be null')

    def test_tipo_is_not_blank(self):
        self.serializer_data['tipo_documento'] = ''
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        print(str(serializer.errors['tipo_documento'][0]), 'This field may not be blank')
