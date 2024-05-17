from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Alerta
from .views import send_sse

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    
@receiver(post_save, sender=Alerta)
def handle_new_alert(sender, instance, created, **kwargs):
    if created:
        send_sse('{"mensaje": "Nueva alerta creada"}')