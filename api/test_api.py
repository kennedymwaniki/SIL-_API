from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import json
import pytest

from .models import Customer, Orders
from .serializers import CustomerSerializer, OrderSerializer


@pytest.mark.integration
class APIEndToEndTests(APITestCase):
    """
    End-to-end tests for API functionality
    """

    def setUp(self):
        """Set up test data and authenticate"""
        self.client = APIClient()

        # Create a test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )

        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )

        # Set authentication cookie
        self.client.cookies['access_token'] = 'test_access_token'

        # Create test orders
        self.order1 = Orders.objects.create(
            customer=self.customer,
            total_amount=1000.00
        )

        self.order2 = Orders.objects.create(
            customer=self.customer,
            total_amount=2000.00
        )

        # Setup authentication patch
        self.auth_patcher = patch(
            'api.authentication.CookieAuthentication.authenticate')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = (self.user, None)

    def tearDown(self):
        """Clean up after tests"""
        self.auth_patcher.stop()

    def test_customer_retrieval(self):
        """Test that a customer can retrieve their profile"""
        url = reverse('customer-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['phone_number'], self.customer.phone_number)

    def test_customer_update(self):
        """Test that a customer can update their profile"""
        url = reverse('customer-detail', kwargs={'pk': self.customer.id})
        data = {'phone_number': '+254711222333'}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.phone_number, '+254711222333')

    def test_orders_listing(self):
        """Test that a customer can see their orders"""
        url = reverse('order-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verify order details
        order_amounts = [order['total_amount'] for order in response.data]
        self.assertIn('1000.00', order_amounts)
        self.assertIn('2000.00', order_amounts)

    def test_order_creation_with_notification(self):
        """Test creating an order with a notification"""
        url = reverse('order-list')
        data = {'total_amount': '3000.00'}  # String, not float

        # Patch both SMS utilities to prevent actual SMS sending
        # UPDATED: Use the correct signal path from api.signals module
        with patch('api.signals.send_order_confirmation_sms') as mock_sms, \
             patch('api.utils.send_sms') as mock_base_sms:
            mock_sms.return_value = True  # Simulate successful SMS sending
            mock_base_sms.return_value = {'SMSMessageData': {
                'Recipients': [{'status': 'Success'}]}}

            # Ensure the authentication is working
            self.mock_auth.return_value = (self.user, None)

            # Use format='json' to ensure proper content type
            response = self.client.post(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['total_amount'], '3000.00')
            self.assertTrue(Orders.objects.filter(total_amount=3000.00).exists())
            
            # Verify SMS was called
            self.assertTrue(mock_sms.called)

    def test_order_confirmation_sms(self):
        """Test that creating an order triggers a confirmation SMS"""
        url = reverse('order-list')
        data = {'total_amount': '4000.00'}  # String, not float

        # UPDATED: Use the correct signal path from api.signals module
        with patch('api.signals.send_order_confirmation_sms') as mock_confirm_sms, \
             patch('api.utils.send_sms') as mock_send_sms:
            mock_send_sms.return_value = {'SMSMessageData': {
                'Recipients': [{'status': 'Success'}]}}
            mock_confirm_sms.return_value = True

            # Ensure authentication is working
            self.mock_auth.return_value = (self.user, None)

            # Use format='json' to ensure proper content type
            response = self.client.post(url, data, format='json')
            
            # Print response for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data if hasattr(response, 'data') else 'No data'}")

            # Verify order was created
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify an order with this amount was created
            self.assertTrue(Orders.objects.filter(total_amount=4000.00).exists())
            
            # Verify the SMS sending function was called
            self.assertTrue(mock_confirm_sms.called)

    def test_authenticated_user_operations(self):
        """Test that only authenticated users can access protected endpoints"""
        # Remove authentication
        self.mock_auth.return_value = None

        # Try to access customer list
        response = self.client.get(reverse('customer-list'))
        self.assertIn(response.status_code,
                      (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        # Try to access orders list
        response = self.client.get(reverse('order-list'))
        self.assertIn(response.status_code,
                      (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        # Try to create an order
        data = {'total_amount': 5000.00}
        response = self.client.post(reverse('order-list'), data)
        self.assertIn(response.status_code,
                      (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


@pytest.mark.acceptance
class GoogleOAuthIntegrationTests(TestCase):
    """Tests for the Google OAuth integration flow"""

    def setUp(self):
        self.client = APIClient()

    def test_login_redirect(self):
        """Test that the login page redirects to Google OAuth"""
        response = self.client.get(reverse('google_login'), follow=False)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue('accounts.google.com' in response.url)
        self.assertTrue('oauth2/auth' in response.url)

    @patch('requests.post')
    @patch('requests.get')
    def test_oauth_callback_creates_user_and_customer(self, mock_get, mock_post):
        """Test that the callback creates a user and customer when needed"""
        # Mock token response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'id_token': 'mock_id_token'
        }

        # Mock user info response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'given_name': 'New',
            'family_name': 'User',
        }

        # Call the callback with a mock code
        response = self.client.get(
            reverse('google_callback'),
            {'code': 'mock_code', 'state': 'mock_state'}
        )

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['success'])

        # Verify user is created
        self.assertTrue(User.objects.filter(
            email='newuser@example.com').exists())

        # Verify customer profile is created
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(Customer.objects.filter(user=user).exists())

        # Verify tokens are stored
        customer = Customer.objects.get(user=user)
        self.assertEqual(customer.access_token, 'mock_access_token')
        self.assertEqual(customer.refresh_token, 'mock_refresh_token')

    @patch('requests.post')
    @patch('requests.get')
    def test_oauth_callback_existing_user(self, mock_get, mock_post):
        """Test callback with an existing user"""
        # Create existing user
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='password'
        )

        customer = Customer.objects.create(
            user=user,
            phone_number='+254700000000',
            access_token='old_token',
            refresh_token='old_refresh'
        )

        # Mock token response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'id_token': 'mock_id_token'
        }

        # Mock user info response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'email': 'existing@example.com',  # Same email as existing user
            'name': 'Existing User',
            'given_name': 'Existing',
            'family_name': 'User',
        }

        # Call the callback
        response = self.client.get(
            reverse('google_callback'),
            {'code': 'mock_code', 'state': 'mock_state'}
        )

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['success'])

        # Verify tokens are updated
        customer.refresh_from_db()
        self.assertEqual(customer.access_token, 'new_access_token')
        self.assertEqual(customer.refresh_token, 'new_refresh_token')


@pytest.mark.integration
class OrderAPITests(APITestCase):
    """
    Tests for Order API functionality
    """

    def setUp(self):
        """Set up test data and authenticate"""
        self.client = APIClient()
        self.url = reverse('order-list')

        # Create a test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )

        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )

        # Set authentication cookie
        self.client.cookies['access_token'] = 'test_access_token'

        # Create test orders
        self.order1 = Orders.objects.create(
            customer=self.customer,
            total_amount=1000.00
        )

    def test_create_order(self):
        """Test creating a new order"""
        new_order_data = {
            'total_amount': '500.00'  # Ensure this is a string
        }
        
        # Mock authentication to return our test user
        # Also patch the SMS utility to prevent actual SMS sending
        # UPDATED: Use the correct signal path from api.signals module
        with patch('api.authentication.CookieAuthentication.authenticate') as mock_auth, \
             patch('api.signals.send_order_confirmation_sms') as mock_sms, \
             patch('api.utils.send_sms') as mock_base_sms:
            mock_auth.return_value = (self.user, None)
            mock_sms.return_value = True
            mock_base_sms.return_value = {'SMSMessageData': {
                'Recipients': [{'status': 'Success'}]}}
            
            # Use format='json' to ensure proper content type
            response = self.client.post(self.url, new_order_data, format='json')
            
            # Print response for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data if hasattr(response, 'data') else 'No data'}")
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Orders.objects.count(), 2)
            self.assertEqual(response.data['total_amount'], '500.00')
            self.assertIsNotNone(response.data['order_code'])
