from django.contrib import admin

from app.product.models import BrandCar, ModelCar

admin.site.register(BrandCar)
admin.site.register(ModelCar)