from django.db.models.signals import post_save
from django.dispatch import receiver
from trades.models import Order
from strader.utils import constants


@receiver(post_save, sender=Order, dispatch_uid='account_balance_update')
def update_account_balance(sender, instance, created, **kwargs):
    """
    Update user account's balance to reflect the order

    @Note:
        For this puprose, assume all orders are FILLED.
    """

    if created and instance.status.code != constants.FAILED:
        # account balance should update when order is FILLED or PARTIAL
        # but for now consider only FILLED.
        # stock share of the user should also be updated.

        account = instance.account
        stock_code = instance.stock
        stock_share, _ = instance.account.shares.get_or_create(stock=stock_code)

        order_val = instance.total_value
        order_type = instance.order_type.code

        if order_type == constants.BUY:
            account.available_bp -= order_val
            stock_share.quantity += instance.quantity
            stock_share.total_value += order_val
        elif order_type == constants.SELL:
            account.available_bp += order_val
            stock_share.quantity -= instance.quantity
            stock_share.total_value -= order_val

        account.save()
        stock_share.save()
