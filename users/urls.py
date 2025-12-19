from django.urls import path
from .views import RegisterAPIView, ProfileAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]