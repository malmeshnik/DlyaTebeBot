from rest_framework import serializers
from .models import Gender, Product, ProductImage, Banner, Brand, ProductVariant


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


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ("id", "name", "slug", "image", "description")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "gender", "image")

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "volume_ml",
            "price",
            "old_price",
            "is_active",
        )

class ProductSerializer(serializers.ModelSerializer):
    gender = GenderSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "image",
            "gender",
            "brand",
            "price",
            "old_price",
            "characteristics",
            "is_available",
            "available",
            "sort_order",
            "gallery",
            "variants",
        )