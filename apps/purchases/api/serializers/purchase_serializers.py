from decimal import Decimal
from rest_framework import serializers
from apps.purchases.models import Purchase, Item


class ItemPurchaseListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        # validated_data es una lista
        instance_items = super().create(validated_data)
        # una vez se crea la instancia que se realice el incrememento
        for item in instance_items:
            item.increment_stock()
        return instance_items

    def update(self, instance, validated_data):
        # una vez entramos aca decrementamos lo que agregaron los items
        for item in instance:
            item.decrement_stock()
            # item.state = False
            # item.save()
            item.delete()
        # como usamos el delete significa que borraremos todos los items
        # ahora crearemos unos nuevos
        instance_items = super().create(validated_data)
        for item in instance_items:
            item.increment_stock()
        # instance.increment_stock()
        return instance_items

    def delete(self, instance):
        for item in instance:
            item.decrement_stock()
            item.delete()
        return instance

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

class PurchaseReadSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    def get_items(self, instance):
        qs = Item.objects.filter(state=True)
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

        # item for item has diferent product
        if len(set(item['producto'] for item in value)) != len(value):
            raise serializers.ValidationError("Solo un item por producto", code='not_same_product')
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
        instance = super().create(validated_data)
        # seteamos el objeto purchase para cada item
        for item in items:
            item['compra'] = instance

        # creamos los items y ejecutamos la logica
        self.fields['items'].create(items)
        return instance

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance = super().update(instance, validated_data)
        actual_items = instance.items.all()

        # relacionamos los nuevos items con la compra
        for item in items_data:
            item['compra'] = instance

        # enviamos los items actuales y ejecutamos la logica
        self.fields['items'].update(actual_items, items_data)
        return instance

    def destroy(self, instance):
        # los items actuales los eliminamos.
        instance.state = False
        instance.save()
        actual_items = instance.items.all()
        # actual_items.update(state=False)
        # mandamos a reducir el stock que agregaron
        self.fields['items'].delete(actual_items)
        return instance
