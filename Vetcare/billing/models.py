from django.db import models
from django.conf import settings


#Add this app to settings when you work on it
User = settings.AUTH_USER_MODEL

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed')
    ], default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

