from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import Account


class AccountTests(APITestCase):

    def test_create_account(self):
        """
        Accounts should be automatically created after creating a user.
        """

        user = User.objects.create(username='test-user')
        user.set_password('testuserpass1234')

        assert Account.objects.get(user=user) is not None
