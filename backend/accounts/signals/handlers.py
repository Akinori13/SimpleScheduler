from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, Profile

@receiver(post_save, sender=User)
def create_profile_with_signup(sender, instance, update_fields, **kwargs):
    if instance.is_active == True:
        Profile.objects.get_or_create(user=instance)