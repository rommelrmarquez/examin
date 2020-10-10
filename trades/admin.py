from django.contrib import admin
from trades.models import Stock, Order, OrderType, OrderStatus, StockShare


admin.site.register(Stock)
admin.site.register(Order)
admin.site.register(OrderType)
admin.site.register(OrderStatus)
admin.site.register(StockShare)
