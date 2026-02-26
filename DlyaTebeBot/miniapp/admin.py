from django.contrib import admin
from django.utils.html import format_html
from .models import Gender, Brand, Product, ProductImage, Banner, ProductVariant, Order


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("volume_ml", "price", "old_price", "is_active")
    ordering = ("volume_ml",)

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
        "image_preview_small",
        "name",
        "brand",
        "price",
        "is_available",
        "sort_order",
        "created_at",
    )

    list_filter = ("brand", "gender", "is_available")
    search_fields = ("name", "brand__name")
    list_editable = ("price", "is_available", "sort_order")
    ordering = ("sort_order", "-created_at")
    prepopulated_fields = {"slug": ("name",)}

    readonly_fields = (
        "image_preview",
        "site_preview",
        "created_at",
    )

    inlines = [ProductVariantInline]

    fieldsets = (
        ("📦 Основна інформація", {
            "fields": (
                "name",
                "slug",
                "gender",
                "brand",
            )
        }),

        ("💰 Ціна та наявність", {
            "fields": (
                "price",
                "old_price",
                "is_available",
                "available",
                "sort_order",
            )
        }),

        ("📝 Опис", {
            "fields": ("characteristics",),
        }),

        ("🖼 Фото", {
            "fields": (
                "image",
                "image_preview",
            ),
        }),

        ("🔗 Додатково", {
            "classes": ("collapse",),
            "fields": (
                "site_preview",
                "created_at",
            ),
        }),
    )

    def image_preview_small(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" style="border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview_small.short_description = "Фото"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="border-radius:10px;" />',
                obj.image.url
            )
        return "Немає фото"

    def site_preview(self, obj):
        return format_html(
            '<a href="/products/{}/" target="_blank" '
            'style="padding:8px 12px;background:#0d6efd;'
            'color:white;border-radius:6px;text-decoration:none;">'
            'Переглянути на сайті</a>',
            obj.slug,
        )
    site_preview.short_description = "Сторінка товару"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("image", "link")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_name",
        "product",
        "variant",
        "price",
        "colored_status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("product__name", "id")
    ordering = ("-created_at",)

    readonly_fields = (
        "product",
        "variant",
        "price",
        "telegram_chat_id",
        "created_at",
    )

    def colored_status(self, obj):
        colors = {
            "new": "#3B82F6",
            "in_progress": "#F59E0B",
            "done": "#10B981",
            "canceled": "#EF4444",
        }

        color = colors.get(obj.status, "#000")

        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )

    colored_status.short_description = "Статус"

    def has_add_permission(self, request):
        return False