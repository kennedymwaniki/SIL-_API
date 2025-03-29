import os
import africastalking
from dotenv import load_dotenv
from django.contrib.auth.models import User
load_dotenv()

username = os.getenv("AFRICASTALKING_USERNAME")
api_key = os.getenv("AFRICASTALKING_API_KEY")
sender_id = os.getenv("")
africastalking.initialize(username, api_key)

sms = africastalking.SMS


def send_sms(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print(f"SMS sent to {phone_number}: {response}")
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None


def send_order_confirmation_sms(customer, order):
    message = f"Hello {customer.user.firstname}, your order with code {order.order_code} has been confirmed. Thank you for shopping with us!"
    return send_sms(customer.phone_number, message)
