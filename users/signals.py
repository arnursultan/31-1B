from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User


@receiver(pre_save, sender=User)
def sync_staff_flag(sender, instance, **kwargs):
    if instance.is_superuser:
        instance.is_staff = True
        return

    if instance.role == "admin":
        instance.is_staff = True
    else:
        instance.is_staff = False
