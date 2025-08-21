import sys
import os
import africastalking
from dotenv import load_dotenv
from django.contrib.auth.models import User
load_dotenv()


username = os.getenv("AFRICASTALKING_USERNAME")
api_key = os.getenv("AFRICASTALKING_API_KEY")
sender_id = os.getenv("AFRICASTALKING_SENDERID")

# Only initialize if not in test mode
is_testing = 'test' in sys.argv or 'pytest' in sys.modules

if not is_testing:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
else:

    class MockSMS:
        @staticmethod
        def send(message, recipients):
            return {"SMSMessageData": {"Recipients": [{"status": "Success"}]}}

    sms = MockSMS()


def send_sms(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print(f"SMS sent to {phone_number}: {response}")
        print(f"Response from sending the message: {response}")
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None


def send_order_confirmation_sms(customer, order):
    print("sending confirmation SMS.....")
    message = f"Hello {customer.user.first_name}, your order with code {order.order_code} has been confirmed. Thank you for shopping with us!"
    return send_sms(customer.phone_number, message)
