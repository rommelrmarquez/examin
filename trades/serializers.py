from rest_framework import serializers
from strader.utils import constants
from trades.models import Order, Stock, OrderType, OrderStatus, StockShare


class StockShareSerializer(serializers.ModelSerializer):
    """Serializer for user's stock shares"""

    class Meta:
        model = StockShare
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for user's order for list method"""
    stock = serializers.CharField(source='stock.code')
    status = serializers.CharField(source='status.code')
    order_type = serializers.CharField(source='order_type.code')

    class Meta:
        model = Order
        exclude = ('account', 'id',)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""

    stock = serializers.SlugRelatedField(queryset=Stock.objects.all(),
                                         slug_field='code')
    order_type = serializers.SlugRelatedField(queryset=OrderType.objects.all(),
                                              slug_field='code')
    total_value = serializers.FloatField(required=False)
    status = serializers.CharField(source='status.code', required=False)

    class Meta:
        model = Order
        exclude = ('account', )

    def compute_total_value(self, order):
        """
            Compute the total order value. For this purpose, assume orders
            are always fully executed.
        """

        return order['quantity'] * order['price']

    def validate(self, data):
        """Override to check current balance and available shares"""

        ret = super().validate(data)
        total_value = self.compute_total_value(ret)
        account = self.context['request'].user.account
        stock = ret['stock']
        order_type = ret['order_type'].code
        quantity = ret['quantity']
        stock_share, _ = account.shares.get_or_create(stock=stock)

        # check available BP if order type is BUY
        if order_type == constants.BUY and total_value > account.available_bp:
            raise serializers.ValidationError({'details':
                                               'Not enough buying power.'})

        # check if current stock shares is enough for SELL
        if order_type == constants.SELL and quantity > stock_share.quantity:
            raise serializers.ValidationError({'details':
                                               'Not enough shares.'})

        ret.update(total_value=total_value)
        return ret


    def create(self, data):
        """Perform business logic in posting the order"""

        # status will depend on the third party(?) API we will call
        # to execute the order. The status will depend on their return
        # For this purpose, all transaction will be FULLy executed.

        status = OrderStatus.objects.get(code=constants.FILLED)
        data.update(
            # total_value=self.compute_total_value(data),
            account=self.context['request'].user.account,
            status=status
        )

        return super().create(data)
