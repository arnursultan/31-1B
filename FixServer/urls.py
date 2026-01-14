from django.contrib import admin
from django.urls import path, include

from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from users.views import (
    ThrottledTokenObtainPairView,
    OAuthSuccessView,
    ProfileView,
    AdminDashboardView,
    SuperUserOnlyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    path("admin/", admin.site.urls),

    path("auth/", include("social_django.urls")),
    path("auth/success/", OAuthSuccessView.as_view(), name="oauth_success"),

    path("api/token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/profile/", ProfileView.as_view(), name="profile"),
    path("api/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("api/superuser/", SuperUserOnlyView.as_view(), name="superuser_only"),

    path(
        "auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "auth/password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

