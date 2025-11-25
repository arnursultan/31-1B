from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from app.product.models import BrandCar, ModelCar
from app.product.serializers import BrandCarSerializers, ModelCarSerilaizer

class BrandCarListCreateAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    queryset = BrandCar.objects.all().order_by('title')
    serializer_class = BrandCarSerializers
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

class BrandCarRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BrandCar.objects.all()
    serializer_class = BrandCarSerializers
    permission_classes = [IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Brand deleted"}, status=status.HTTP_200_OK)

class ModelCarListCreateAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = ModelCar.objects.all().select_related('brand').all().order_by('title')
    serializer_class = ModelCarSerilaizer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

class ModelCarRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelCar.objects.select_related('brand').all()
    serializer_class = ModelCarSerilaizer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Model deleted"}, status=status.HTTP_200_OK)

class BrandCarViewSet(viewsets.ModelViewSet):
    queryset = BrandCar.objects.all().order_by('title')
    serializer_class = BrandCarSerializers
    permission_classes = [IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Brand deleted"}, status=status.HTTP_200_OK)

        @action(detail=True, methods=['get', 'post'], url_path='models')
        def models(self, request, pk=None):
            brand = self.get_object()

            if request.method == 'GET':
                qs = ModelCar.objects.filter(brand=brand).order_by('title')
                serializer = ModelCarSerilaizer(qs, many=True, context={'request': request})
                return Response(serializer.data)

            serializer = ModelCarSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(brand=brand)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ModelCarViewSet(viewsets.ModelViewSet):
    queryset = ModelCar.objects.select_related('brand').all().order_by('title')
    serializer_class = ModelCarSerilaizer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Model deleted"}, status=status.HTTP_200_OK)