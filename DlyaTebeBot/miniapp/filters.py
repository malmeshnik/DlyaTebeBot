from django_filters import rest_framework as filters
from .models import Product


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name="categories__slug",
        lookup_expr="exact"
    )

    brand = CharInFilter(
        field_name="brand__slug",
        lookup_expr="in"
    )

    price_min = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )
    price_max = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    search = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "price_min",
            "price_max",
            "search",
        ]
