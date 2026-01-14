from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework import status
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

    def get(self, request):
        return render(
            request,
            "auth/oauth_success.html",
            {
                "access": request.session.get("access"),
                "refresh": request.session.get("refresh"),
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
            "detail": "Admin access granted",
            "users_count": User.objects.count(),
        })


class SuperUserOnlyView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        return Response({
            "detail": "Superuser access granted",
        })

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

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

        return Response(
            {"detail": "If email exists, reset link was sent"},
            status=status.HTTP_200_OK,
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

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

        return Response(
            {"detail": "Password successfully updated"},
            status=status.HTTP_200_OK,
        )
