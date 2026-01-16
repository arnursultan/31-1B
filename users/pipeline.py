from .tasks import send_welcome_email

def send_welcome_email_pipeline(strategy, user=None, **kwargs):
    if user and user.last_login is None:
        send_welcome_email.delay(user.email)
