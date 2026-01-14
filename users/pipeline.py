from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import send_welcome_email

def generate_jwt_pipeline(strategy, user=None, **kwargs):
    refresh = RefreshToken.for_user(user)
    strategy.session_set("access", str(refresh.access_token))
    strategy.session_set("refresh", str(refresh))

def send_welcome_email_pipeline(strategy, user=None, **kwargs):
    if user and user.last_login is None:
        send_welcome_email.delay(user.email)
