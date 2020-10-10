from django.urls import path, include
from rest_framework import routers
from trades import views as trades


router = routers.DefaultRouter()
router.register('orders', trades.OrderViewSet, basename='orders')
router.register('summary', trades.OrderSummaryViewSet, basename='order-summary')
router.register(r'shares/(?P<scope>\w+)', trades.StockShareSummaryViewSet,
                basename='shares')


urlpatterns = [
    path('', include(router.urls)),
]
