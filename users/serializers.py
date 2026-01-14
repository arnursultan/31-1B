from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
        )

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=8,
        write_only=True,
    )

    def validate(self, data):
        uid = self.context.get("uid")
        token = self.context.get("token")

        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Invalid reset link")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is invalid or expired")

        self.context["user"] = user
        return data
