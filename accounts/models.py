from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    """User model extension for additional data"""

    available_bp = models.FloatField(max_length=6, default=0.0)
    alloted_bp = models.FloatField(max_length=6, default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='account')

    class Meta:
        db_table = 'account_account'

    def __str__(self):
        return self.user.username
