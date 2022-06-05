from rest_framework import serializers

from apps.purchases.models import Product

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ('state', 'created_date', 'modified_date', 'deleted_date')

    def validate_price(self, value):
        # solo validara si es que se envia
        if value == "" or value is None:
            raise serializers.ValidationError("El precio debe ser mayor que 0")
        return value
