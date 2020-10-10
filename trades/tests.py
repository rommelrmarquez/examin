from django.core.management import call_command
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trades.models import Order, OrderType, Stock, OrderStatus, StockShare
from accounts.models import Account


class OrderTestCase(APITestCase):

    def setUp(self):
        for fixture in ['orders', 'status', 'stocks']:
            call_command('loaddata', fixture, verbosity=0)

    def set_auth_token_header(self):
        """Get auth token for api calls"""

        username = 'test-user'
        passwd = 'testuserpass1234'
        user = User.objects.create(username=username)
        user.set_password(passwd)
        user.save()

        assert Account.objects.get(user=user) is not None
        url = reverse('token_obtain_pair')
        res = self.client.post(url,
                               data={'username': username, 'password': passwd})
        self.client.credentials(HTTP_AUTHORIZATION=
                                f"Bearer {res.data['access']}")
        return user

    def test_fixtures(self):
        """Test if fixtures are loadded"""

        self.assertEqual(OrderType.objects.count(), 2,
                         'Incorrect order type count')
        self.assertEqual(Stock.objects.count(), 3,
                         'Incorrect stocks count')
        self.assertEqual(OrderStatus.objects.count(), 3,
                         'Incorrect statuses count')

    def test_apis_wo_auth(self):
        """User should be authenticated"""

        # Order list API
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Order summary API
        url = reverse('order-summary-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Order create API
        url = reverse('orders-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Shares list/summary API
        url = reverse('shares-list', args=['summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse('shares-list', args=['all'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_list(self):
        """Valid order list request"""

        user = self.set_auth_token_header()

        # Order list API
        # User has no order
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # User has orders
        data = [
            {
                'stock': Stock.objects.get(code='AAPL'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            },
        ]
        data_obj = [Order(**item) for item in data]
        _ = Order.objects.bulk_create(data_obj)

        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(data))

    def test_get_orders_by_stock(self):
        """Valid order list request but filtered by specific stock"""

        user = self.set_auth_token_header()

        # Order list API
        # User has no order
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # User has orders
        data = [
            {
                'stock': Stock.objects.get(code='AAPL'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            },
            {
                'stock': Stock.objects.get(code='GOOG'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            }
        ]
        data_obj = [Order(**item) for item in data]
        _ = Order.objects.bulk_create(data_obj)

        url = reverse('orders-list')
        response = self.client.get(url, data={'stock': 'AAPL'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.data
        self.assertEqual(len(res_data), 1)
        self.assertEqual(res_data[0]['stock'], 'AAPL')


    def test_order_total_value(self):
        """Valid order summary request for all orders"""

        user = self.set_auth_token_header()
        data = [
            {
                'stock': Stock.objects.get(code='AAPL'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            },
            {
                'stock': Stock.objects.get(code='GOOG'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            }
        ]
        data_obj = [Order(**item) for item in data]
        _ = Order.objects.bulk_create(data_obj)

        url = reverse('order-summary-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        total_value = sum([order['total_value'] for order in data])
        self.assertEqual(response.data['total_value'], total_value)

    def test_order_total_value_by_stock(self):
        """Valid order summary request for orders of specific stock"""

        user = self.set_auth_token_header()
        data = [
            {
                'stock': Stock.objects.get(code='AAPL'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.5,
                'account': user.account
            },
            {
                'stock': Stock.objects.get(code='GOOG'),
                'order_type': OrderType.objects.get(code='BUY'),
                'total_value': 18.75,
                'status': OrderStatus.objects.get(code='FILLED'),
                'quantity': 15.0,
                'price': 1.25,
                'account': user.account
            }
        ]
        data_obj = [Order(**item) for item in data]
        _ = Order.objects.bulk_create(data_obj)

        url = reverse('order-summary-list')
        response = self.client.get(url, data={'stock': 'GOOG'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        total_value = sum([order['total_value'] for order in data
                           if order['stock'].code == 'GOOG'])
        self.assertEqual(response.data['total_value'], total_value)

    def test_buy_order(self):
        """Create valid buy order"""

        user = self.set_auth_token_header()

        # set account buying power
        account = user.account
        account.available_bp = 1000
        account.save()

        data = {
            'stock': 'GOOG',
            'quantity': 15,
            'price': 1.25,
            'order_type': 'BUY'
        }

        # Order create API
        url = reverse('orders-list')
        response = self.client.post(url, data=data)
        # order created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # account balance should've been updated
        acc = Account.objects.get(user=user)
        self.assertEqual(acc.available_bp, 981.25)

        # stock shares should've been updated
        shares = StockShare.objects.get(account=acc)
        self.assertEqual(shares.quantity, 15.0)
        self.assertEqual(shares.total_value, 18.75)
        self.assertEqual(shares.stock.code, 'GOOG')

    def test_sell_order(self):
        """Create valid sell order"""

        user = self.set_auth_token_header()

        # create stock shares
        shares_data = {
            'account': user.account,
            'quantity': 15,
            'total_value': 18.75,
            'stock': Stock.objects.get(code='GOOG')
        }
        StockShare.objects.create(**shares_data)

        data = {
            'stock': 'GOOG',
            'quantity': 10,
            'price': 1.25,
            'order_type': 'SELL'
        }

        # Order create API
        url = reverse('orders-list')
        response = self.client.post(url, data=data)
        # order created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # account balance should've been updated
        acc = Account.objects.get(user=user)
        self.assertEqual(acc.available_bp, 12.5)

        # stock shares should've been updated
        shares = StockShare.objects.get(account=acc)
        self.assertEqual(shares.quantity, 5.0)
        self.assertEqual(shares.total_value, 6.25)
        self.assertEqual(shares.stock.code, 'GOOG')

    def test_invalid_buy_order(self):
        """Create invalid buy order. Insufficient buying power"""

        _ = self.set_auth_token_header()

        data = {
            'stock': 'GOOG',
            'quantity': 15,
            'price': 1.25,
            'order_type': 'BUY'
        }

        # Order create API
        url = reverse('orders-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['details'][0]),
                         'Not enough buying power.')

    def test_invalid_sell_order(self):
        """Create invalid sell order. Insufficient shares on account"""

        _ = self.set_auth_token_header()

        data = {
            'stock': 'GOOG',
            'quantity': 15,
            'price': 1.25,
            'order_type': 'SELL'
        }

        # Order create API
        url = reverse('orders-list')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['details'][0]),
                         'Not enough shares.')
