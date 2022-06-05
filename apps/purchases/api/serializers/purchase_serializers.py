from collections import OrderedDict
from decimal import Decimal
from itertools import product
from rest_framework import serializers
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField
from datetime import datetime
from apps.purchases.models import Purchase, Item


class ItemPurchaseListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        cantidad = validated_data['cantidad']
        producto = validated_data['producto']
        producto.stock += cantidad
        instance = super().create(validated_data)
        instance.increment_stock()

        return instance

    def update(self, instance, validated_data):
        print("hola")
        return instance

    def delete(self, instance):
        pass

class ItemPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'producto', 'cantidad', 'incluye_igv',
                  'total_item')
        list_serializer_class = ItemPurchaseListSerializer

    def validate_cantidad(self, value):
        if value == 0:
            raise serializers.ValidationError("La cantidad no puede ser 0", code='cant_zero')
        return value

    def create(self, validated_data):
        cantidad = validated_data['cantidad']
        producto = validated_data['producto']
        producto.stock += cantidad
        instance = super().create(validated_data)
        instance.increment_stock()

        return instance

    def update(self, instance, validated_data):
        print("hola")
        return instance


class PurchaseReadSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    def get_items(self, instance):
        qs = Item.objects.filter(state=True,
                                 compra__id=instance.id)
        data = ItemPurchaseSerializer(qs, many=True).data
        return data

    class Meta:
        model = Purchase
        fields = ('id', 'proveedor', 'tipo_documento',
                  'num_documento', 'fecha_documento',
                  'serie', 'correlativo', 'total',
                  'fecha_vencimiento', 'moneda', 'items')

    def update(self, instance, validated_data):
        pass

    def create(self, instance, validated_data):
        pass

class PurchaseWriteSerializer(serializers.ModelSerializer):

    # como es una lista many=True
    items = ItemPurchaseSerializer(many=True)

    class Meta:
        model = Purchase
        fields = ('proveedor', 'tipo_documento', 'num_documento',
                  'fecha_documento', 'fecha_vencimiento', 'moneda',
                  'total', 'items')

    def validate_items(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Debe enviar al menos un item", code='no_items')
        return value

    def validate_total(self, value):
        if any(chr.isalpha() for chr in value):
            raise serializers.ValidationError("El valor contiene caracteres no numericos", code=2)

        value = round(Decimal(value), 2)
        return value

    def validate_num_documento(self, value):
        if not ("-" in value):
            raise serializers.ValidationError("El número de documento debe tener un guion", code='guion')

        serie, correlativo = value.split("-")

        if len(serie) != 4:
            raise serializers.ValidationError("El valor de serie no tiene 4 caracteres", code='serie4')

        """
        if serie[0] != 'F' and serie[0] != 'B' and serie[0] != 'E':
            raise serializers.ValidationError("El valor de la serie no comienza con B o F", code='BorForE')
        """

        if any(chr.isalpha() for chr in correlativo):
            raise serializers.ValidationError("El valor de correlativo no tiene numeros", code='corr_non_num')
        return value

    def validate_fecha_vencimiento(self, value):
        fecha_documento = self.initial_data.get('fecha_documento')
        if value == '' or value is None:
            value = fecha_documento
        return value

    def validate(self, attrs):
        """Esto genera serie y correlativo"""
        serie, correlativo = attrs.get('num_documento').split('-')
        attrs['serie'] = serie
        attrs['correlativo'] = correlativo

        """
        suma = Decimal(0.00)
        for value in attrs['items']:
            suma = suma + value.get('total_item')
        if suma != attrs['total']:
            raise serializers.ValidationError(
                {"total": "La sumatoria de precio items no coincide"}, code='dif_sum')
        """
        suma = 0
        for value in attrs['items']:
            suma = suma + int(100*value.get('total_item'))

        if suma != int(100*attrs['total']):
            raise serializers.ValidationError(
                {"total": "La sumatoria de precio items no coincide"}, code='dif_sum')

        if attrs['fecha_documento'] > attrs['fecha_vencimiento']:
            raise serializers.ValidationError(
                {"fecha_vencimiento": "La fecha de vencimiento es menor que la fecha de documento"}, 
                code='fven<fdoc')
        return attrs

    def create(self, validated_data):
        items = validated_data.pop('items')
        # dividimos el campo num_documento en serie y correlativo
        serie, correlativo = validated_data['num_documento'].split('-')
        validated_data['serie'] = serie
        validated_data['correlativo'] = correlativo
        instance = super().create(validated_data)

        # seteamos el objeto purchase para cada item
        for item in items:
            item['compra'] = instance

        # creamos los items
        print(self.fields['items'])
        self.fields['items'].create(items)
        return instance

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance = super().update(instance, validated_data)

        # los items actuales los eliminamos y creamos unos nuevos
        # aca solo acceso a todos los items que se agregaron
        actual_items = (instance.items).all()

        # desactivo los items y reduzco el stock que habian agregado
        actual_items.update(state=False)

        # reducimos el stock que se tenia en la compra
        """
        for item in actual_items:
            item.producto.stock -= item.cantidad
        """
        for item in items_data:
            item['compra'] = instance

        # creamos todos los items
        self.fields['items'].update(items_data, validated_data)
        return instance
