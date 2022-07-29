from decimal import Decimal
from rest_framework import serializers
from apps.purchases.models import Purchase, Item, Supplier


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
        # y lo eliminamos
        for item in instance:
            item.decrement_stock()
            # item.producto.save()
            item.delete()
        # creamos los nuevos items
        instance_items = super().create(validated_data)
        # una vez se crea la instancia que se realice el incremento
        for item in instance_items:
            item.increment_stock()
            # item.producto.save()
        return instance_items

    def delete(self, instance):
        for item in instance:
            item.decrement_stock()
            # realizamos un cambio al stock hay que guardarlo
            item.delete()
        return instance


class ItemPurchaseSerializer(serializers.ModelSerializer):
    total_item = serializers.DecimalField(max_digits=6, decimal_places=2)
    igv = serializers.DecimalField(max_digits=6, decimal_places=2)

    def to_representation(self, instance):
        return{
            "id": instance.id,
            "cantidad": instance.cantidad,
            "igv": instance.igv/100 if instance is not None else instance.igv,
            "total_item": instance.total_item/100,
        }

    class Meta:
        model = Item
        fields = ('id', 'producto', 'cantidad', 'igv',
                  'total_item')
        list_serializer_class = ItemPurchaseListSerializer

    def validate_cantidad(self, value):
        if value == 0:
            raise serializers.ValidationError("La cantidad no puede ser 0",
                                              code='cant_zero')
        return value

    def validate_total_item(self, value):
        return int(value*100)

    # Lo mas importante en la compra es el total y la cantidad
    def validate(self, attrs):
        if attrs["igv"]:
            igv_int = attrs["total_item"]*18/118
            if int(attrs["igv"]*100) != round(igv_int):
                raise serializers.ValidationError("El IGV no coincide",
                                                  code='dif_igv')
            attrs['igv'] = attrs['igv']*100
        return attrs

    def delete(self, instance):
        pass


class SupplierPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = ('id', 'legal_name')


class PurchaseListSerializer(serializers.ModelSerializer):
    proveedor = SupplierPurchaseSerializer()

    class Meta:
        model = Purchase
        fields = ('id', 'proveedor', 'tipo_documento',
                  'num_documento', 'fecha_documento',
                  'serie', 'correlativo', 'total',
                  'fecha_vencimiento', 'moneda')


class PurchaseReadSerializer(serializers.ModelSerializer):

    proveedor = SupplierPurchaseSerializer()
    items = ItemPurchaseSerializer(many=True)

    """
    items = serializers.SerializerMethodField()
        def get_items(self, instance):
        qs = Item.objects.filter(compra__id=instance.id)
        data = ItemPurchaseSerializer(qs, many=True).data
        return data
    """

    class Meta:
        model = Purchase
        fields = ('id', 'proveedor', 'tipo_documento',
                  'num_documento', 'fecha_documento',
                  'serie', 'correlativo', 'total',
                  'fecha_vencimiento', 'moneda', 'items')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
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
        if any(char.isalpha() for char in value):
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

        if any(char.isalpha() for char in correlativo):
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

        suma = 0
        for value in attrs['items']:
            suma = suma + value.get('total_item')

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
        # actual_items = Item.objects.filter(compra__id=instance.id)
        actual_items = instance.items.all()
        instance = super().update(instance, validated_data)

        # relacionamos los nuevos items con la compra
        for item in items_data:
            item['compra'] = instance

        # enviamos los items actuales con los items para crear los nuevos
        self.fields['items'].update(actual_items, items_data)
        return instance

    def destroy(self, instance):
        # los items actuales los eliminamos.
        instance.state = False
        instance.save()
        # obtenemos sus items para enviarlos a eliminar
        actual_items = instance.items.all()
        # mandamos a reducir el stock que agregaron
        self.fields['items'].delete(actual_items)
        return instance
