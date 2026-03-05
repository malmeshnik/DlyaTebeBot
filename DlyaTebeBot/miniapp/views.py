import json
from asgiref.sync import async_to_sync
from loguru import logger

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField, Prefetch
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Gender, Product, Brand, Banner, ProductVariant, Order
from .serializers import (
    GenderSerializer,
    ProductSerializer,
    BrandSerializer,
    BannerSerializer,
    OrderCreateSerializer
)
from .filters import ProductFilter
from .telegram_auth import check_telegram_auth, check_viber_auth
from bot.tg_bot.utils import send_alerts_for_admin
from bot.tg_bot.repo import TgUserRepo
from bot.models import TgUser
from viber_bot.repo import ViberUserRepo
from viber_bot.models import ViberUser

class GenderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing categories.
    """

    queryset = Gender.objects.all().order_by("id")
    serializer_class = GenderSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Products list & detail.
    Default ordering: sort_order ASC
    """
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    lookup_field = "slug"

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_class = ProductFilter
    search_fields = ("name",)

    ordering_fields = (
        "sort_order",
        "price",
        "name",
        "created_at",
    )

    def get_queryset(self):
        return (
            Product.objects.filter(is_available=True)
            .annotate(
                sort_priority=Case(
                    When(sort_order__gt=0, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "sort_priority",
                "sort_order",
                "id",
            )
            .select_related("brand", "gender")
            .prefetch_related(
                    Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(is_active=True)
                )
            )
        )


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Brand.objects.all().order_by("id")

        gender = self.request.query_params.get("gender")

        if gender:
            queryset = queryset.filter(gender__slug=gender)

        return queryset

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()

class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=["post"])
    def create_order(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data.get("product_id")
        variant_id = serializer.validated_data.get("variant_id")
        user = request.user

        logger.info(f"Creating order: product_id={product_id}, variant_id={variant_id}, user={user.id}")

        product = Product.objects.get(id=product_id)
        variant = None
        price = product.price

        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
            price = variant.price


        order_data = {
            "product": product,
            "variant": variant,
            "price": price
        }

        if isinstance(user, TgUser):
            order_data["tg_user"] = user

        elif isinstance(user, ViberUser):
            order_data["viber_user"] = user

        order = Order.objects.create(**order_data)

        product_name = product.name
        volume = variant.volume_ml if variant else None
        product_photo = product.image.path if product.image else None

        async_to_sync(send_alerts_for_admin)(order, product_name, volume, product_photo)

        return Response(
            {"order_id": order.id},
            status=status.HTTP_201_CREATED
        )
    
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def telegram_auth(request):
    request.throttle_scope = "telegram_auth"
    logger.info(f"Telegram auth request data: {request.data}")

    init_data = request.data.get("initData")

    if not init_data:
        logger.error(f"initData is required for Telegram auth")
        return Response(
            {"error": "initData is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = check_telegram_auth(init_data, settings.BOT_TOKEN)

    if not data:
        logger.error(f"Invalid Telegram data")
        return Response(
            {"error": "Invalid Telegram data"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_data = data.get("user", None)

        if not user_data:
            logger.error(f"Invalid user data in Telegram auth")
            return Response(
                {"error": "Invalid user data"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Telegram auth data: {user_data}")
    except Exception:
        logger.error(f"Invalid user data")
        return Response(
            {"error": "Invalid user data"},
            status=status.HTTP_400_BAD_REQUEST
        )

    telegram_id = user_data.get("id")
    if not telegram_id:
        return Response(
        {"error": "Invalid user id"},
        status=status.HTTP_400_BAD_REQUEST
    )

    user, _ = TgUserRepo.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
        }
    )

    refresh = RefreshToken()

    refresh["telegram_id"] = user.telegram_id
    refresh["user_id"] = user.id

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
        }
    })

@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def viber_auth(request):

    request.throttle_scope = "viber_auth"

    miniapp_token = request.data.get("token")

    if not miniapp_token:
        return Response(
            {"error": "Invalid auth data"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = ViberUserRepo.get_by_miniapp_token(miniapp_token)

    if not user:
        return Response(
            {"error": "Invalid token"},
            status=403
        )

    refresh = RefreshToken()

    refresh["viber_id"] = user.viber_id
    refresh["user_id"] = user.id

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "viber_id": user.viber_id
        }
    })