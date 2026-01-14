from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When, Value, IntegerField
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Product, Brand, Model, Banner
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    BrandSerializer,
    ModelSerializer,
    BannerSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing categories.
    """

    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
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
            .select_related("brand", "model")
            .prefetch_related("categories")
        )


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Brand.objects.all().order_by("id")

        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(category__slug=category)

        return queryset


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ModelSerializer

    def get_queryset(self):
        qs = Model.objects.all()

        brand = self.request.query_params.get("brand")
        category = self.request.query_params.get("category")

        if brand:
            qs = qs.filter(brand__slug=brand)

        if category:
            qs = qs.filter(category__slug=category)

        return qs

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()