from django.db.models import Sum
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from trades.models import Stock, Order, StockShare
from trades.serializers import (OrderSerializer,
                                OrderListSerializer,
                                StockShareSerializer)
from trades.filters import OrderFilter
from strader.utils import constants


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API for listing placed orders (GET) and placing sell or buy orders (POST)

    - Parameters:
        (GET)
            - `stock` str (optional) filter the list by stock code
            - `order_type` str (optional) filter the list by order type
                                Possible values: BUY, SELL
            - `stock_name` str (optional) filter the list by stock name

        (POST)
            `data` dict-like object containing:
                - `stock` str (required) stock code
                - `quantity` float (required) number of shares
                - `price` float (required) desired price for the order
                - `order_type` str (required) BUY or SELL
    """

    model = Order
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    filter_class = OrderFilter
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        """Override to get corresponding order of a user"""

        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        account = self.request.user.account
        return Order.objects.filter(account=account)

    def get_serializer_class(self):
        """Override to get appropriate serializer based on request method"""

        if self.action in ['list', 'retrieve']:
            return OrderListSerializer
        else:
            return OrderSerializer


class OrderSummaryViewSet(viewsets.GenericViewSet):
    """
        API for the total value invested by a user. The order summary can be
        filtered by specific stock.
    """

    model = Order
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def compute_total_value(self, order_type, stock=None):
        """
            Compute total value invested.

        Parameters:
            - `order_type` str BUY or SELL
            - `stock` str (default: None) Use to filter specific stock

        Return:
            total invested value
        """

        filters = {
            'order_type__code': order_type,
            'status__code': constants.FILLED,
            'account': self.request.user.account
        }
        if stock:
            filters['stock__code'] = stock

        q = Order.objects.filter(**filters).aggregate(total=Sum('total_value'))
        return q['total'] or 0.0

    def list(self, request, *args, **kwargs):
        """
        API for the total value invested by a user. The order summary can be
        filtered by specific stock.

        - Parameters:
            - `stock` str (optional) filter the summary by stock code
        """

        stock = request.GET.get('stock', None)
        if stock:
            buys = self.compute_total_value(constants.BUY, stock)
        else:
            buys = self.compute_total_value(constants.BUY)

        summary = {'total_value': buys}
        return Response(summary, status=status.HTTP_200_OK)


class StockShareSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API for the total value a user in their portfolio.
    """

    model = StockShare
    queryset = StockShare.objects.all()
    serializer_class = StockShareSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override to get corresponding shares of a user"""

        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        account = self.request.user.account
        return StockShare.objects.filter(account=account, total_value__gt=0)

    def list(self, request, scope=None):
        """
        API for the total value a user in their portfolio.

        - Parameters
            - `scope` str Possible values: `summary` or `all`
            If scope == summary, return the total value in user's portfolio,
            If scope == all, return the list of stocks shares the user own.
        """

        qs = self.get_queryset()
        if scope == 'summary':
            total = qs.aggregate(total=Sum('total_value'))['total'] or 0.0
            return Response({'total_investment': total}, status=200)
        else:
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
