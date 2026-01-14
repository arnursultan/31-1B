from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        return f"login-{ip}"

class PasswordResetThrottle(SimpleRateThrottle):
    scope = "password_reset"

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        return f"password-reset-{ip}"
