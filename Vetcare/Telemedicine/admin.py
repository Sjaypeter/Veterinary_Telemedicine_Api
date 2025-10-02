from django.contrib import admin
from . models import Appointment,MedicalRecord,PetProfile,OwnerProfile, Vetprofile
# Register your models here.

admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(PetProfile)
admin.site.register(OwnerProfile)
admin.site.register(Vetprofile)