from rest_framework import serializers

from apps.purchases.models import Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('producto', 'cantidad', 'compra')
