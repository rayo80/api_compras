from rest_framework.serializers import ValidationError
from django.test import TestCase
from apps.purchases.models import Supplier
from apps.purchases.api.serializers.supplier_serializers import SupplierSerializer


class SupplierSerializerTest(TestCase):

    def setUp(self):
        # Creacion de una Instancia
        self.supplier_attributes = {
            "tipo_documento": '1',
            "num_documento": '15256698',
            "legal_name": "Jhon Doe",
            "address": "48764 Howard Forge Apt. 421\nVanessaside, PA 19763",
            "phone": "996666363",
            "email": "elenasheremetev@skillion.org",
        }

        self.supplier = Supplier.objects.create(**self.supplier_attributes)
        self.serializer = SupplierSerializer(instance=self.supplier)

        # Json ingresado
        self.serializer_data = {
            "tipo_documento": '1',
            "num_documento": '15256699',
            "legal_name": "Jhon ",
            "address": "48764 Howard Forge Apt. 421\nVanessaside, PA 19763",
            "phone": "996666363",
            "email": "elenasheremetev@skillion.org",
        }

    def test_contains_expected_fields(self):
        # Instancia genera los campos esperados a serializar
        data = self.serializer.data
        self.assertEqual(set(data.keys()),
                         {'tipo_documento', 'num_documento', 'legal_name', 'address', 'phone', 'email', 'cod_proveedor',
                          'type_person', 'id'})

    def test_validate_num_documento_is_numeric(self):
        self.serializer_data['num_documento'] = 'valormalo'
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors['num_documento'][0]),
                         'El valor contiene caracteres no numericos')
        self.assertEqual(serializer.errors['num_documento'][0].code, 'no_num')

    def test_validate_num_documento_with_tipo_6(self):
        self.serializer_data['tipo_documento'] = '6'
        self.serializer_data['num_documento'] = '415263'
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['num_documento'][0].code, 'lenruc_11')

    def test_validate_num_documento_with_tipo_1(self):
        self.serializer_data['tipo_documento'] = '1'
        self.serializer_data['num_documento'] = '415263'
        serializer = SupplierSerializer(data=self.serializer_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['num_documento'][0].code, 'lendni_8')

    def test_name_is_not_none(self):
        self.serializer_data['legal_name'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(str(er.exception.detail['legal_name'][0].code), 'null')

    def test_name_is_not_blank(self):
        self.serializer_data['legal_name'] = ''
        serializer = SupplierSerializer(data=self.serializer_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(str(er.exception.detail['legal_name'][0].code), 'blank')

    def test_num_is_not_none(self):
        self.serializer_data['num_documento'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors['num_documento'][0]), 'This field may not be null.')

    def test_num_is_not_blank(self):
        self.serializer_data['num_documento'] = ''
        serializer = SupplierSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors['num_documento'][0]), 'This field may not be blank.')

    # Aca solo testeo que me error el serializador y no error del modelo
    def test_tipo_is_not_none(self):
        self.serializer_data['tipo_documento'] = None
        serializer = SupplierSerializer(data=self.serializer_data)
        with self.assertRaises(ValidationError) as er:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(er.exception.detail['tipo_documento'][0].code, 'null')
