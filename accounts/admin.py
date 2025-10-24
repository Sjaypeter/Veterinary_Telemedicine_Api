from django.contrib import admin
from . models import ClientProfile, Vetprofile, CustomUser
# Register your models here.

admin.site.register(Vetprofile)
admin.site.register(ClientProfile)
admin.site.register(CustomUser)