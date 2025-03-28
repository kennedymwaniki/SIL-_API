from rest_framework.routers import DefaultRouter
from .views import CustomerViewset, OrderViewset
router = DefaultRouter()

router.register(r'customers',CustomerViewset, basename='customer')
router.register(r'orders', OrderViewset, basename='order')


urlpatterns = router.urls