from django.urls import path

from .views import (
    ProfileView,
    AdminDashboardView,
    SuperUserOnlyView,
)

urlpatterns = [

    path("profile/", ProfileView.as_view(), name="profile"),

    path("admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("superuser/", SuperUserOnlyView.as_view(), name="superuser_only"),
]
