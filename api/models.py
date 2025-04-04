from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.get_full_name()}"
    


class Orders(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    order_code = models.CharField(max_length=20, unique=True ,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.order_code:
            # generate a unique order code when order is created
            self.order_code = self.generate_order_code()
        super().save(*args, **kwargs)

    def generate_order_code(self):
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
