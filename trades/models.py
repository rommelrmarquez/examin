from django.db import models
from accounts.models import Account


class Stock(models.Model):
    """Class for tradeable stocks"""

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    class Meta:
        db_table = 'trades_stock'

    def __str__(self):
        return self.code


class OrderType(models.Model):
    """Class for BUY or SELL"""

    action = models.CharField(max_length=12)
    code = models.CharField(max_length=8)

    class Meta:
        db_table = 'trades_order_type'

    def __str__(self):
        return self.code


class OrderStatus(models.Model):
    """Class for status of the orders"""

    code = models.CharField(max_length=12)
    description = models.TextField()

    class Meta:
        db_table = 'trades_order_status'
        verbose_name_plural = 'Order Statuses'

    def __str__(self):
        return self.code


class Order(models.Model):
    """Class for trade orders"""

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT,
                              related_name='orders')
    quantity = models.FloatField(max_length=3)
    price = models.FloatField(max_length=3, default=0.0)
    total_value = models.FloatField(max_length=3, default=0.0)

    # audit fields
    date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT,
                               related_name='orders')
    order_type = models.ForeignKey(OrderType, on_delete=models.PROTECT,
                                  related_name='orders')

    class Meta:
        db_table = 'trades_order'

    def __str__(self):
        return self.stock.code


class StockShare(models.Model):
    """Class for the current stock shares a user has"""

    stock = models.ForeignKey(Stock, on_delete=models.PROTECT,
                              related_name='shares')
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='shares')
    quantity = models.FloatField(max_length=3, default=0.0)
    total_value = models.FloatField(max_length=3, default=0.0)

    class Meta:
        db_table = 'trades_stock_share'

    def __str__(self):
        return f'{self.stock.code}/{self.quantity}'
