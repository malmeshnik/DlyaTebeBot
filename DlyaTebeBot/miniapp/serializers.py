from rest_framework import serializers
from .models import Gender, Product, ProductImage, Banner, Brand, ProductVariant, WheelPrize, WheelSpin


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


class OrderCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product not found")
        return value

    def validate_variant_id(self, value):
        if value and not ProductVariant.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product variant not found")
        return value


class WheelPrizeSerializer(serializers.ModelSerializer):
    """Серіалізатор для відображення призів колеса"""

    class Meta:
        model = WheelPrize
        fields = ['id', 'name', 'color', 'lose', 'sort_order']


class WheelSpinSerializer(serializers.ModelSerializer):
    """Серіалізатор для історії прокрутів"""
    prize_name = serializers.CharField(source='prize.name', read_only=True)
    platform = serializers.CharField(read_only=True)

    class Meta:
        model = WheelSpin
        fields = ['id', 'code', 'prize_name', 'is_claimed', 'created_at', 'platform']
        read_only_fields = ['code', 'created_at']