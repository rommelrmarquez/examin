from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from accounts.models import Account


@receiver(post_save, sender=User, dispatch_uid='create_account')
def create_account(sender, instance, created, **kwargs):
    """Create account when user is created"""

    if created:
        Account.objects.create(user=instance)
