from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .models import Customer


class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None

        try:
            customer = Customer.objects.get(access_token=access_token)
            return (customer.user, None)
        except Customer.DoesNotExist:
            raise AuthenticationFailed('Invalid access token')
