from django.contrib import admin
from .models import Vetprofile,Appointment,MedicalRecords,PetProfile,OwnerProfile
# Register your models here.
admin.site.register(Vetprofile)
admin.site.register(Appointment)
admin.site.register(MedicalRecords)
admin.site.register(PetProfile)
admin.site.register(OwnerProfile)