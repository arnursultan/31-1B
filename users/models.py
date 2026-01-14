from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
