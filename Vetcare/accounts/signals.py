from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import Vetprofile, ClientProfile, CustomUser

User = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'vet':
            Vetprofile.objects.create(user=instance)
        else:
            ClientProfile.objects.create(user=instance)
