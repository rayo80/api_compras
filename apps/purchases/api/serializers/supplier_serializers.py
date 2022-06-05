from rest_framework import serializers

from apps.purchases.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        exclude = ('state', 'created_date', 'modified_date', 'deleted_date')

    def validate_num_documento(self, value):
        documento = self.initial_data.get('tipo_documento')
        if value.isnumeric() is False:
            raise serializers.ValidationError("El valor contiene caracteres no numericos", code=0)
        if documento == "6" and len(value) != 11:
            raise serializers.ValidationError("El ruc debe contener 11 caracteres", code=1)
        if documento == "1" and len(value) != 8:
            raise serializers.ValidationError("El DNI debe contener 8 caracteres", code=2)
        return value
