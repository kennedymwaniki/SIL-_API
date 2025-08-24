from rest_framework import serializers
from .models import Customer, Orders


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['id', 'customer', 'order_date', 'order_code', 'total_amount']
        read_only_fields = ['order_code']
        extra_kwargs = {
            'customer': {'required': False}
        }


class CustomerSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number',
                  'access_token', 'refresh_token', 'orders']
        read_only_fields = ['access_token', 'refresh_token']
