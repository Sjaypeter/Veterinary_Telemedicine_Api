from django.contrib import admin
from . models import OwnerProfile, Vetprofile, CustomUser
# Register your models here.

admin.site.register(Vetprofile)
admin.site.register(OwnerProfile)
admin.site.register(CustomUser)