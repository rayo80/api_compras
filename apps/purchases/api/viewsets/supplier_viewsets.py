from apps.purchases.api.serializers.supplier_serializers import \
    SupplierSerializer
from rest_framework import viewsets


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    queryset = SupplierSerializer.Meta.model.objects.filter(state=True)

