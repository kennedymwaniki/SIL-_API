from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Orders
from .utils import send_order_confirmation_sms

@receiver(post_save, sender=Orders)
def send_confirmation_on_order_create(sender, instance, created, **kwargs):
    """Send confirmation SMS when a new order is created"""
    if created and instance.customer.phone_number:  # Only send if phone number exists
        send_order_confirmation_sms(instance.customer, instance)