from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_welcome_email(self, email):
    subject = "Добро пожаловать"
    text_content = "Добро пожаловать на нашу платформу"
    html_content = render_to_string("emails/welcome.html")

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_reset_password_email(self, email, reset_link):
    subject = "Сброс пароля"
    text_content = f"Нажмите на ссылку, чтобы сбросить пароль:\n\n{reset_link}"
    html_content = render_to_string(
        "emails/reset_password.html",
        {"reset_link": reset_link},
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
