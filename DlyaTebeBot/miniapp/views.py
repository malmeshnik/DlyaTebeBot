from asgiref.sync import async_to_sync

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When, Value, IntegerField, Prefetch
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Gender, Product, Brand, Banner, ProductVariant, Order
from .serializers import (
    GenderSerializer,
    ProductSerializer,
    BrandSerializer,
    BannerSerializer
)
from .filters import ProductFilter
from bot.tg_bot.utils import send_alerts_for_admin

class GenderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing categories.
    """

    queryset = Gender.objects.all().order_by("id")
    serializer_class = GenderSerializer
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Products list & detail.
    Default ordering: sort_order ASC
    """

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
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def create_order(self, request):
        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        variant = None
        price = product.price

        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                price = variant.price
            except ProductVariant.DoesNotExist:
                pass

        order = Order.objects.create(
            product=product,
            variant=variant,
            price=price
        )

        product_name = product.name

        async_to_sync(send_alerts_for_admin)(order, product_name, variant.volume_ml)

        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)