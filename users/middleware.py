from django.core.cache import cache
from django.http import JsonResponse
import time

class OAuthLoginRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/auth/login/"):
            ip = request.META.get("REMOTE_ADDR")
            key = f"oauth-login-{ip}"
            count = cache.get(key, 0) + 1
            if count > 10:
                return JsonResponse({"detail": "Too many OAuth attempts"}, status=429)
            cache.set(key, count, 60)
        return self.get_response(request)

class OAuthCallbackRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/auth/complete/"):
            ip = request.META.get("REMOTE_ADDR")
            key = f"oauth-callback-{ip}"
            count = cache.get(key, 0) + 1
            if count > 20:
                return JsonResponse({"detail": "Too many callbacks"}, status=429)
            cache.set(key, count, 60)
        return self.get_response(request)
