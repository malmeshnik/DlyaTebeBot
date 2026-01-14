from rest_framework import serializers
from .models import Category, Product, ProductImage, Banner, Brand, Model


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("image", "link")

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("image",)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "image", "description")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "category", "image")


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ("id", "name", "slug")


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    model = ModelSerializer(read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "image",
            "categories",
            "brand",
            "model",
            "price",
            "old_price",
            "characteristics",
            "is_available",
            "available",
            "sort_order",
            "gallery",
        )

    def get_category(self, obj):
        return obj.category.name if obj.category else None
