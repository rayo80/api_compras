from rest_framework import viewsets
from apps.purchases.api.serializers.item_serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = ItemSerializer.Meta.model.objects.filter(state=True)
