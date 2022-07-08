from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Directory, User

@receiver(post_save, sender=User)
def notify_user(sender, instance, created, **kwargs):
    if created:
        Directory.objects.create(name="root", owner=instance, parent=None)