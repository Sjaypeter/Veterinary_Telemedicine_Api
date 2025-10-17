from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from . models import Vetprofile

@receiver(post_save, sender=User)
def create_vet_profile(sender, instance, created, **kwargs):
    # Only create for veterinarian users
    if created and hasattr(instance, 'user_type'):
        if instance.user_type == 'Veterinarian':  
            Vetprofile.objects.get_or_create(user=instance)