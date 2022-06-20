from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
# from rest_framework.decorators import action
from apps.purchases.api.serializers.purchase_serializers import (
    PurchaseReadSerializer,
    PurchaseWriteSerializer,
)
from django.db import transaction
# from django.db import transaction

class PurchaseViewSet(viewsets.ModelViewSet):

    serializer_class = PurchaseReadSerializer
    queryset = PurchaseWriteSerializer.Meta.model.objects.filter(state=True)

    @transaction.atomic(using='default')
    def create(self, request, *args, **kwargs):
        serializer = PurchaseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase_created = serializer.save()
        return Response(PurchaseReadSerializer(purchase_created).data,
                        status=status.HTTP_201_CREATED)

    @transaction.atomic(using='default')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PurchaseWriteSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase_updated = serializer.save()
        print(purchase_updated)
        return Response(PurchaseReadSerializer(purchase_updated).data,
                        status=status.HTTP_201_CREATED)

    @transaction.atomic(using='default')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PurchaseWriteSerializer()
        serializer.destroy(instance)
        return Response({"message": "Eliminado"},
                        status=status.HTTP_204_NO_CONTENT)
        # compra.anular_items
        # delete items decrement stock

    """
    @transaction.atomic(using='default')
    @action(detail=True, methods=['POST'])
    def anular(self, request, pk=None):
        instance = self.get_object()
        instance.anular_items()
        serializer = PurchaseWriteSerializer(instance)
        purchase_updated = serializer.save()
    """
