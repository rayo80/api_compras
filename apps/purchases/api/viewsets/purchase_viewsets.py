from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
# from rest_framework.decorators import action
from apps.purchases.api.serializers.purchase_serializers import (
    PurchaseReadSerializer,
    PurchaseWriteSerializer,
    PurchaseListSerializer,
)
from django.db import transaction


class PurchaseViewSet(viewsets.ModelViewSet):

    serializer_class = PurchaseReadSerializer
    queryset = PurchaseWriteSerializer.Meta\
        .model.objects.filter(state=True)\
        .select_related('proveedor')\

    # reemplazable por un MYMODELVIEWSET HOOK list---#
    # Como deseo que la list no traiga los items cambio de serializador

    action_serializers = {
        'retrieve': PurchaseReadSerializer,
        'list': PurchaseListSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(self.action, self.serializer_class)
        return super(PurchaseViewSet, self).get_serializer_class()

    # -------------#

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
        return Response(PurchaseReadSerializer(purchase_updated).data,
                        status=status.HTTP_201_CREATED)

    @transaction.atomic(using='default')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PurchaseWriteSerializer()
        serializer.destroy(instance)
        return Response({"message": "Compra eliminada se reducira stock"},
                        status=status.HTTP_204_NO_CONTENT)

    """
    @transaction.atomic(using='default')
    @action(detail=True, methods=['POST'])
    def anular(self, request, pk=None):
        instance = self.get_object()
        instance.anular_items()
        serializer = PurchaseWriteSerializer(instance)
        purchase_updated = serializer.save()
    """
