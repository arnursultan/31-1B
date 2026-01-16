from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_encode,
)

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdmin, IsSuperUser
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .tasks import send_reset_password_email
from .throttles import LoginThrottle, PasswordResetThrottle

User = get_user_model()

class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]

class OAuthSuccessView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        user = request.user

        if not user or not user.is_authenticated:
            return HttpResponse(
                "OAuth failed or user not authenticated",
                status=401,
            )

        refresh = RefreshToken.for_user(user)

        return render(
            request,
            "auth/oauth_success.html",
            {
                "email": user.email,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            "detail": "Предоставлен доступ администратора",
            "users_count": User.objects.count(),
        })

class SuperUserOnlyView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        return Response({
            "detail": "Доступ суперпользователя предоставлен",
        })

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def get(self, request):
        return render(request, "auth/password_reset_request.html")

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_link = (
                f"http://127.0.0.1:8000"
                f"/auth/password/reset/confirm/{uid}/{token}/"
            )

            send_reset_password_email.delay(user.email, reset_link)

        return render(
            request,
            "auth/password_reset_request.html",
            {"success": True},
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        return render(
            request,
            "auth/password_reset_confirm.html",
            {
                "uid": uidb64,
                "token": token,
            },
        )

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            context={
                "uid": uidb64,
                "token": token,
            },
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.context["user"]
        user.set_password(serializer.validated_data["password"])
        user.save()

        return render(
            request,
            "auth/password_reset_confirm.html",
            {"success": True},
        )
