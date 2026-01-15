from django.contrib import admin
from django.utils.html import format_html
from .models import Gender, Brand, Product, ProductImage, Banner


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "gender")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="100" />', obj.image.url)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "sort_order",
        "price",
        "is_available",
        "created_at",
    )
    list_filter = ("brand", "gender", "is_available")
    search_fields = ("name", "gender_name", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    readonly_fields = ("image_preview", "site_preview")
    list_editable = ("price", "is_available", "sort_order")
    ordering = ("sort_order", "-created_at")

    def image_preview(self, obj):
        return format_html('<img src="{}" width="100" />', obj.image.url)

    def site_preview(self, obj):
        return format_html(
            '<a href="/products/{}/" target="_blank">View on site</a>', obj.slug
        )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("image", "link")