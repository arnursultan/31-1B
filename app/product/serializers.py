from rest_framework import serializers
from app.product.models import BrandCar, ModelCar

class BrandCarSerializers(serializers.ModelSerializer):
    class Meta:
        model = BrandCar
        fields = ['id', 'title', 'type_car']

class ModelCarSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = ModelCar
        fields = ["id", 'title', 'brand']