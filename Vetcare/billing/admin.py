from django.contrib import admin
from . models import Transaction, Subscription
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Subscription)