from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(email):
    send_mail(
        "Добро пожаловать",
        "Добро пожаловать на нашу платформу",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_reset_password_email(self, email, reset_link):
    send_mail(
        subject="Сброс пароля",
        message=f"Нажмите на ссылку ниже, чтобы сбросить пароль:\n\n{reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )