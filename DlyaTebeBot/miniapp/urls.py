from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenderViewSet,
    ProductViewSet,
    BannerViewSet,
    BrandViewSet,
    OrderViewSet,
    telegram_auth,
    viber_auth,
    wheel_prizes,
    wheel_check_eligibility,
    wheel_spin,
)

router = DefaultRouter()
router.register(r"genders", GenderViewSet, basename="genders")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"banners", BannerViewSet, basename="banners")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("telegram-auth/", telegram_auth, name="telegram-auth"),
    path("viber-auth/", viber_auth, name="viber-auth"),
    path("wheel/prizes/", wheel_prizes, name="wheel-prizes"),
    path("wheel/check-eligibility/", wheel_check_eligibility, name="wheel-check-eligibility"),
    path("wheel/spin/", wheel_spin, name="wheel-spin"),
    path("", include(router.urls)),
]