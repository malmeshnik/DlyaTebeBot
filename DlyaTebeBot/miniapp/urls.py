from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    BrandViewSet,
    ModelViewSet,
    BannerViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"models", ModelViewSet, basename="models")
router.register(r"banners", BannerViewSet, basename="banners")

urlpatterns = [
    path("", include(router.urls)),
]
