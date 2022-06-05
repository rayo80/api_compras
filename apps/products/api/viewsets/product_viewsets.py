from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from apps.products.api.serializers.product_serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = ProductSerializer.Meta.model.objects.filter(state=True)
