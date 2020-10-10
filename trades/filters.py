import django_filters
from trades.models import Order


class OrderFilter(django_filters.FilterSet):
    stock = django_filters.CharFilter(field_name='stock__code',
                                      lookup_expr='iexact')
    stock_name = django_filters.CharFilter(field_name='stock__name',
                                           lookup_expr='icontains')
    order_type = django_filters.CharFilter(field_name='order_type__code',
                                           lookup_expr='iexact')

    class Meta:
        model = Order
        fields = ('stock', 'order_type')
