from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json
from unittest.mock import patch, MagicMock
import uuid
import pytest

from .models import Customer, Orders
from .serializers import CustomerSerializer, OrderSerializer
from .utils import send_sms, send_order_confirmation_sms
from .authentication import CookieAuthentication

# Unit Tests
@pytest.mark.unit
class CustomerModelTests(TestCase):
    def setUp(self):
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
    
    def test_customer_creation(self):
        """Test that customer can be created with proper attributes"""
        self.assertEqual(self.customer.user.username, 'testuser')
        self.assertEqual(self.customer.phone_number, '+254700000000')
        self.assertEqual(str(self.customer), 'Test User')

@pytest.mark.unit
class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000'
        )
        self.order = Orders.objects.create(
            customer=self.customer,
            total_amount=1000.00
        )
    
    def test_order_creation(self):
        """Test that order is created with proper attributes and gets an order code"""
        self.assertIsNotNone(self.order.order_code)
        self.assertTrue(self.order.order_code.startswith('ORD-'))
        self.assertEqual(self.order.total_amount, 1000.00)
        self.assertEqual(self.order.customer, self.customer)

    def test_order_code_generation(self):
        """Test that a unique order code is generated"""
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678123456781234567812345678')
            order = Orders(customer=self.customer, total_amount=500.00)
            order_code = order.generate_order_code()
            self.assertEqual(order_code, 'ORD-12345678')

# SMS utility tests
@pytest.mark.unit
class SMSUtilityTests(TestCase):
    @patch('api.utils.sms')
    def test_send_sms(self, mock_sms):
        """Test that SMS can be sent"""
        mock_sms.send.return_value = {'SMSMessageData': {'Recipients': [{'status': 'Success'}]}}
        
        result = send_sms('+254700000000', 'Test message')
        
        mock_sms.send.assert_called_once_with('Test message', ['+254700000000'])
        self.assertIsNotNone(result)
    
    @patch('api.utils.send_sms')
    def test_order_confirmation_sms(self, mock_send_sms):
        """Test that order confirmation SMS is sent with correct message"""
        user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            first_name='Test',
            password='testpassword'
        )
        customer = Customer.objects.create(
            user=user,
            phone_number='+254700000000'
        )
        
        
        order = Orders.objects.create(
            customer=customer,
            total_amount=1000.00
        )
        
        # Reset the mock to clear the call that happened during order creation
        mock_send_sms.reset_mock()
        
        # Now test our function directly
        send_order_confirmation_sms(customer, order)
        
        expected_message = f"Hello {user.first_name}, your order with code {order.order_code} has been confirmed. Thank you for shopping with us!"
        mock_send_sms.assert_called_once_with(customer.phone_number, expected_message)

# Authentication Tests
@pytest.mark.unit
class CookieAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )
        self.auth = CookieAuthentication()
    
    def test_authenticate_success(self):
        """Test that authentication works with a valid access token"""
        request = MagicMock()
        request.COOKIES = {'access_token': 'test_access_token'}
        
        user, auth = self.auth.authenticate(request)
        
        self.assertEqual(user, self.user)
        self.assertIsNone(auth)
    
    def test_authenticate_failure(self):
        """Test that authentication fails with an invalid access token"""
        request = MagicMock()
        request.COOKIES = {'access_token': 'invalid_token'}
        
        with self.assertRaises(Exception):
            self.auth.authenticate(request)
    
    def test_authenticate_no_token(self):
        """Test that authentication returns None when no token is provided"""
        request = MagicMock()
        request.COOKIES = {}
        
        result = self.auth.authenticate(request)
        
        self.assertIsNone(result)

# Integration Tests
@pytest.mark.integration
class CustomerAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )
        self.url = reverse('customer-list')
        
        # Mock authentication
        self.client.cookies['access_token'] = 'test_access_token'
    
    def test_get_customer_list(self):
        """Test retrieving customer list (should only return the user's own customer record)"""
        # Mock authentication to return our test user
        with patch('api.authentication.CookieAuthentication.authenticate') as mock_auth:
            mock_auth.return_value = (self.user, None)
            
            response = self.client.get(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['phone_number'], '+254700000000')
    
    def test_update_customer(self):
        """Test updating a customer"""
        detail_url = reverse('customer-detail', kwargs={'pk': self.customer.id})
        updated_data = {'phone_number': '+254711111111'}
        
        # Mock authentication to return our test user
        with patch('api.authentication.CookieAuthentication.authenticate') as mock_auth:
            mock_auth.return_value = (self.user, None)
            
            response = self.client.patch(detail_url, updated_data)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.customer.refresh_from_db()
            self.assertEqual(self.customer.phone_number, '+254711111111')

@pytest.mark.integration
class OrderAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='+254700000000',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )
        self.order = Orders.objects.create(
            customer=self.customer,
            total_amount=1000.00
        )
        self.url = reverse('order-list')
        
        # Mock authentication
        self.client.cookies['access_token'] = 'test_access_token'
    
    def test_get_orders(self):
        """Test retrieving a list of orders"""
        # Mock authentication to return our test user
        with patch('api.authentication.CookieAuthentication.authenticate') as mock_auth:
            mock_auth.return_value = (self.user, None)
            
            response = self.client.get(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['total_amount'], '1000.00')
    
    def test_create_order(self):
        """Test creating a new order"""
        new_order_data = {
            'total_amount': '500.00'  # Ensure this is a string, not a float
        }
        
        # Mock authentication to return our test user
        with patch('api.authentication.CookieAuthentication.authenticate') as mock_auth:
            mock_auth.return_value = (self.user, None)
            
            # Use format='json' to ensure proper content type
            response = self.client.post(self.url, new_order_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Orders.objects.count(), 2)
            self.assertEqual(response.data['total_amount'], '500.00')
            self.assertIsNotNone(response.data['order_code'])

# Acceptance Tests - OAuth Flow
@pytest.mark.acceptance
class OAuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    @patch('requests.get')
    @patch('requests.post')
    def test_google_oauth_flow(self, mock_post, mock_get):
        """Test the complete Google OAuth flow"""
        # Mock the token exchange response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'id_token': 'mock_id_token',
        }
        
        # Mock the user info response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'email': 'newuser@example.com',
            'given_name': 'New',
            'family_name': 'User',
            'name': 'New User',
        }
        
        # Test the callback with a mock code
        response = self.client.get(reverse('google_callback'), {'code': 'mock_auth_code'})
        
        # Verify the response (expect redirect status)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/')
        
        # Verify cookies
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        
        # Verify customer was created with tokens
        user = User.objects.get(email='newuser@example.com')
        customer = Customer.objects.get(user=user)
        self.assertEqual(customer.access_token, 'new_access_token')
        self.assertEqual(customer.refresh_token, 'new_refresh_token')
    
    @patch('requests.post')
    def test_token_refresh(self, mock_post):
        """Test refreshing an access token"""
        # Create a user with a refresh token
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        customer = Customer.objects.create(
            user=user,
            phone_number='+254700000000',
            access_token='old_access_token',
            refresh_token='test_refresh_token'
        )
        
        # Mock the refresh token response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'new_access_token',
        }
        
        # Set up cookies
        self.client.cookies['refresh_token'] = 'test_refresh_token'
        
        # Test the refresh endpoint
        response = self.client.post(reverse('refresh_token'))
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
        self.assertTrue(response.json()['success'])
        
        # Verify the access token was updated
        customer.refresh_from_db()
        self.assertEqual(customer.access_token, 'new_access_token')
        
        # Verify the new access token was set as a cookie
        self.assertIn('access_token', response.cookies)
