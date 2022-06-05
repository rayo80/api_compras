from rest_framework.routers import DefaultRouter
from apps.purchases.api.viewsets.purchase_viewsets import PurchaseViewSet
from apps.purchases.api.viewsets.supplier_viewsets import SupplierViewSet

router = DefaultRouter()

router.register(r'purchase', PurchaseViewSet, basename='purchase')
router.register(r'supplier', SupplierViewSet, basename='supplier')

urlpatterns = router.urls
