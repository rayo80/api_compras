from rest_framework import serializers

from apps.purchases.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        exclude = ('state', 'created_date', 'modified_date', 'deleted_date')

    def validate_num_documento(self, value):
        if value.isnumeric() is False:
            raise serializers.ValidationError("El valor contiene caracteres no numericos",
                                              code='no_num')
        return value

    def validate(self, attribs):
        documento = attribs.get('tipo_documento')
        if (documento == "6" or "1") and attribs['num_documento'].isnumeric() is False:
            raise serializers.ValidationError(
                {"num_documento": "El valor contiene caracteres no numericos"},
                code='no_num')

        if documento == "6" and len(attribs['num_documento']) != 11:
            raise serializers.ValidationError(
                {"num_documento": "El RUC debe contener solo 11 caracteres"},
                code='lenruc_11')

        if documento == "1" and len(attribs['num_documento']) != 8:
            raise serializers.ValidationError(
                {"num_documento": "El DNI debe contener 8 caracteres"},
                code='lendni_8')

        return attribs
