from asgiref.sync import async_to_sync
from loguru import logger

from django.urls import reverse
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from unfold.admin import ModelAdmin, TabularInline

from aiogram import Bot

from bot.models import TgUser, TgMessage
from viber_bot.models import ViberUser, ViberMessage
from .models import Gender, Brand, Product, ProductImage, Banner, ProductVariant, Order, WheelPrize, WheelSpin
from .widgets import ColorRadioSelect

class AdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("volume_ml", "price", "old_price", "is_active")
    ordering = ("volume_ml",)

@admin.register(Gender)
class GenderAdmin(ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name", "slug", "gender")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="100" />', obj.image.url)


@admin.register(Product)
class ProductAdmin(ModelAdmin):

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
class BannerAdmin(ModelAdmin):
    list_display = ("image", "link")

def _get_grid_class(count):
    if count == 1:
        return "count-1"
    elif count == 2:
        return "count-2"
    elif count == 3:
        return "count-3"
    elif count == 4:
        return "count-4"
    elif count == 5:
        return "count-5"
    else:
        return "count-many"

def _build_group(messages):
    media_list = [m for msg in messages for m in msg.media.all()]
    count = len(media_list)
    max_visible = 5

    visible_media = media_list[:max_visible] if count > max_visible else media_list
    extra_count = count - max_visible if count > max_visible else 0

    has_text = any(msg.text for msg in messages)

    caption = None
    for m in media_list:
        if getattr(m, 'caption', None):
            caption = m.caption
            break
    if not caption:
        for msg in messages:
            if getattr(msg, 'caption', None):
                caption = msg.caption
                break

    return {
        "messages": messages,
        "first": messages[0],
        "last": messages[-1],
        "media_list": media_list,
        "visible_media": visible_media,
        "extra_count": extra_count,
        "grid_class": _get_grid_class(min(count, 6)),
        "has_text": has_text,
        "caption": caption,
    }

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "order_name",
        "product",
        "variant",
        "price",
        "colored_status",
        "open_chat",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("product__name", "id")
    ordering = ("-created_at",)

    readonly_fields = (
        "product",
        "user",
        "platform",
        "variant",
        "price",
        "telegram_chat_id",
        "created_at",
        "open_chat",
    )

    fields = (
        "product",
        "user",
        "platform",
        "variant",
        "price",
        "status",
        "telegram_chat_id",
        "created_at",
        "open_chat",
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


    def open_chat(self, obj):
        if not obj.user:
            return "-"

        if isinstance(obj.user, TgUser):
            url = reverse("admin:tguser-chat", args=[obj.user.id])
        else:
            url = reverse("admin:viberuser-chat", args=[obj.user.id])

        return format_html(
            '<a href="{}" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'padding: 0.5rem 1rem; background: rgb(59, 130, 246); color: white; '
            'border-radius: 0.5rem; text-decoration: none; font-weight: 500; '
            'font-size: 0.875rem; transition: background 0.2s; white-space: nowrap;" '
            'onmouseover="this.style.background=\'rgb(37, 99, 235)\'" '
            'onmouseout="this.style.background=\'rgb(59, 130, 246)\'">'
            '💬 Відкрити чат</a>',
            url
        )


class WheelPrizeAdminForm(forms.ModelForm):
    class Meta:
        model = WheelPrize
        fields = '__all__'
        widgets = {
            'color': ColorRadioSelect(),
        }


@admin.register(WheelPrize)
class WheelPrizeAdmin(ModelAdmin):
    form = WheelPrizeAdminForm

    list_display = (
        'color_preview',
        'name',
        'probability',
        'sort_order',
        'lose',
        'is_active',
        'spin_count',
    )

    list_editable = ('probability', 'sort_order', 'is_active', 'lose')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('sort_order', 'id')

    fieldsets = (
        ('🎁 Інформація про приз', {
            'fields': ('name', 'probability', 'lose', 'is_active')
        }),
        ('💬 Повідомлення після виграшу', {
            'fields': ('win_image', 'message_text')
        }),
        ('🎨 Оформлення', {
            'fields': ('color', 'sort_order')
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 40px; height: 40px; background-color: {}; '
            'border-radius: 6px; border: 2px solid rgba(0,0,0,0.1);"></div>',
            obj.color
        )
    color_preview.short_description = 'Колір'

    def spin_count(self, obj):
        count = obj.spins.count()
        return format_html(
            '<span style="color: #10B981; font-weight: 600;">{}</span>',
            count
        )
    spin_count.short_description = 'Кількість виграшів'


@admin.register(WheelSpin)
class WheelSpinAdmin(ModelAdmin):
    list_display = (
        'code',
        'prize',
        'user_info',
        'platform',
        'colored_status',
        'created_at',
    )

    list_filter = ('is_claimed', 'created_at', 'prize')
    search_fields = ('code', 'tg_user__username', 'viber_user__name')
    readonly_fields = (
        'code',
        'prize',
        'tg_user',
        'viber_user',
        'session_key',
        'created_at',
        'claimed_at',
    )
    ordering = ('-created_at',)

    fields = (
        'code',
        'prize',
        'tg_user',
        'viber_user',
        'session_key',
        'is_claimed',
        'created_at',
        'claimed_at',
    )

    def has_add_permission(self, request):
        return False

    def user_info(self, obj):
        if obj.tg_user:
            return format_html(
                '<strong>{}</strong><br><small>@{}</small>',
                obj.tg_user.first_name or obj.tg_user.username,
                obj.tg_user.username or 'без username'
            )
        elif obj.viber_user:
            return format_html(
                '<strong>{}</strong>',
                obj.viber_user.name or 'Viber користувач'
            )
        return format_html('<em style="color: #999;">Анонімний</em>')
    user_info.short_description = 'Користувач'

    def colored_status(self, obj):
        if obj.is_claimed:
            return format_html(
                '<span style="color: #10B981; font-weight: 600;">✓ Забрано</span>'
            )
        return format_html(
            '<span style="color: #F59E0B; font-weight: 600;">⏳ Очікує</span>'
        )
    colored_status.short_description = 'Статус'