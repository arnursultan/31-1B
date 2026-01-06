from django.urls import path
from .views import RegisterAPIView, ProfileAPIView, oauth_jwt_view

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('profile/', ProfileAPIView.as_view(), name='profile'),

    path('oauth/jwt', oauth_jwt_view),
]