from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from config import settings
from urllib.parse import urlencode
import urllib
import requests
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError  # Add this import
from .models import Customer, Orders
from .serializers import CustomerSerializer, OrderSerializer
from .authentication import CookieAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

import os
from os import getenv
from dotenv import load_dotenv


load_dotenv()


# Create your views here.
google_oauth_url = "https://accounts.google.com/o/oauth2/auth"


@csrf_exempt
def login(request):
    return JsonResponse({"msg": "Hello there and Welcome, please proceed to accounts/login/ in order to continue"})


def google_login(request):

    redirect_uri = os.getenv('REDIRECT_URI')

    params = {
        'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]['client_id'],
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'offline',  # Required for refresh token
        'prompt': 'consent',  # show the consent dialog
        'include_granted_scopes': 'true'
    }

    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def google_callback(request):
    code = request.GET.get('code')

    if not code:
        return JsonResponse({'error': 'No code received'})

    redirect_uri = os.getenv('REDIRECT_URI')

    # Token exchange parameters
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]['client_id'],
        'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]['secret'],
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'access_type': 'offline'
    }

    # getting the access and refresh token
    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return JsonResponse({
            'error': 'Failed to exchange code for tokens',
            'details': response.json()
        }, status=400)

    tokens = response.json()

    # check if refresh token is present
    if 'refresh_token' not in tokens:
        print("No refresh token was returned")

    # get user info using access token
    userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    userinfo_response = requests.get(userinfo_url, headers=headers)

    if userinfo_response.status_code != 200:
        return JsonResponse({'error': 'Failed to get user info'}, status=400)

    user_info = userinfo_response.json()

    # create a new user based of their email from google
    if user_info.get('email'):
        try:
            # check if a user with the email provided exists in our database
            user = User.objects.get(email=user_info['email'])
        except User.DoesNotExist:

            username = user_info.get('email').split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=user_info['email'],
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', '')
            )

        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={'phone_number': ''}
        )

        # store tokens in the database
        customer.access_token = tokens.get('access_token')
        customer.refresh_token = tokens.get('refresh_token')
        customer.save()

    response = redirect('/profile/')  # Redirect to profile page

    # set https-only cookies for the tokens
    max_age = 3600  #
    response.set_cookie(
        'access_token',
        tokens.get('access_token'),
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite='Lax'
    )

    # refresh token lasts much longer
    response.set_cookie(
        'refresh_token',
        tokens.get('refresh_token'),
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        secure=True,
        samesite='Lax'
    )

    return response


@csrf_exempt
def refresh_token(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return JsonResponse({'error': 'No refresh token'}, status=401)

    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]['client_id'],
        'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]['secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to refresh token'}, status=401)

    tokens = response.json()

    try:
        customer = Customer.objects.get(refresh_token=refresh_token)
        customer.access_token = tokens.get('access_token')
        customer.save()
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Invalid refresh token'}, status=401)

    api_response = JsonResponse({'success': True})
    api_response.set_cookie(
        'access_token',
        tokens.get('access_token'),
        max_age=3600,
        httponly=True,
        secure=True,
        samesite='Lax'
    )

    return api_response


class OrderViewset(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            # Get the customer associated with the user
            customer = Customer.objects.get(user=user)
            return Orders.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Orders.objects.none()

    def perform_create(self, serializer):
        try:
            user = self.request.user
            customer = Customer.objects.get(user=user)

            # Add phone number validation
            if not customer.phone_number:
                raise ValidationError(
                    {"phone_number": "Customer must have a phone number to place orders"})

            serializer.save(customer=customer)
        except Customer.DoesNotExist:
            raise ValidationError(
                {"customer": "Customer not found for this user"})


class CustomerViewset(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:

            existing_customer = Customer.objects.get(user=self.request.user)

            existing_customer.phone_number = serializer.validated_data.get(
                'phone_number', existing_customer.phone_number)
            existing_customer.save()
        except Customer.DoesNotExist:

            serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            # Check if customer already exists
            existing_customer = Customer.objects.get(user=request.user)
            serializer = self.get_serializer(
                existing_customer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        phone_number = request.data.get('phone_number', '')

        if 'phone_number' in request.data and not phone_number:
            return Response(
                {"phone_number": "Phone number cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class ProfileView(APIView):
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)

            response_data = {
                "welcome": f"Welcome, {user.first_name} {user.last_name}",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "customer_id": customer.id,
                "phone_number": customer.phone_number,

            }
            return Response(response_data)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer profile not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )
