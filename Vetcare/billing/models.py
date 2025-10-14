#Django models to track services, invoices, payments, and subscriptions.

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.reference} - {self.user.username}"

    def mark_paid(self):
        self.status = 'paid'
        self.save()

    def mark_failed(self):
        self.status = 'failed'
        self.save()


class Payment(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='payment')
    paystack_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.invoice.reference}"

    def verify(self):
        self.verified = True
        self.paid_at = timezone.now()
        self.save()


