from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from apps.purchases.api.serializers.purchase_serializers import (
    PurchaseReadSerializer,
    PurchaseWriteSerializer,
)


"""
class MultiSerializerViewSet(viewsets.ModelViewSet):
    serializers = {
        'default': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action,
                                    self.serializers['default'])


class PurchaseViewSet(MultiSerializerViewSet):

    serializers = {
        'default': PurchaseReadSerializer,
        'create': PurchaseWriteSerializer,
        'update': PurchaseWriteSerializer,
        "partial_update": PurchaseWriteSerializer,
    }

    queryset = PurchaseWriteSerializer.Meta.model.objects.filter(state=True)
"""


class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseReadSerializer
    queryset = PurchaseWriteSerializer.Meta.model.objects.filter(state=True)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = PurchaseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        purchase_created = serializer.save()
        return Response(PurchaseReadSerializer(purchase_created).data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PurchaseWriteSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase_updated = serializer.save()
        return Response(PurchaseReadSerializer(purchase_updated).data,
                        status=status.HTTP_201_CREATED)
