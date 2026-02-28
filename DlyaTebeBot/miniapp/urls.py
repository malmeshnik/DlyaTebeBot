from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenderViewSet,
    ProductViewSet,
    BannerViewSet,
    BrandViewSet,
    OrderViewSet,
    telegram_auth
)

router = DefaultRouter()
router.register(r"genders", GenderViewSet, basename="genders")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"banners", BannerViewSet, basename="banners")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("telegram-auth/", telegram_auth, name="telegram-auth"),
    path("", include(router.urls)),
]