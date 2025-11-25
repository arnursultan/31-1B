from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.product import views as product_views

router = DefaultRouter()
router.register(r'brands', product_views.BrandCarViewSet, basename='brand')
router.register(r'models', product_views.ModelCarViewSet, basename='model')

urlpatterns = [
    path('', include(router.urls)),
    path('brands/listcreate/', product_views.BrandCarListCreateAPIView.as_view(), name='brand_list_create'),
    path('brands/<int:pk>/', product_views.BrandCarRetrieveUpdateDestroyAPIView.as_view(), name='brand_detail'),
    path('models/listcreate/', product_views.ModelCarListCreateAPIView.as_view(), name='model_list_create'),
    path('models/<int:pk>/', product_views.ModelCarRetrieveUpdateDestroyAPIView.as_view(), name='model_detail')
]
