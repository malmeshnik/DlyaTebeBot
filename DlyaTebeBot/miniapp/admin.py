from asgiref.sync import async_to_sync
from loguru import logger

from django.urls import reverse
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404

from aiogram import Bot

from bot.models import TgUser, TgMessage
from .models import Gender, Brand, Product, ProductImage, Banner, ProductVariant, Order

class AdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

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
class OrderAdmin(admin.ModelAdmin):
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
        "variant",
        "price",
        "telegram_chat_id",
        "created_at",
        "open_chat",
    )

    fields = (
        "product",
        "user",
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
        url = reverse("admin:tguser-chat", args=[obj.user.id])
        return format_html(
            '<a class="button" href="{}">💬 Відкрити чат</a>',
            url
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "chat/<int:user_id>/",
                self.admin_site.admin_view(self.chat_view),
                name="tguser-chat",
            ),
        ]
        return custom_urls + urls

    def chat_view(self, request, user_id):
        user = get_object_or_404(TgUser, pk=user_id)

        messages = (
            user.messages
            .prefetch_related("media")
            .order_by("date")
        )

        raw_groups = []
        current_group = []
        prev_msg = None

        for msg in messages:
            if not prev_msg:
                current_group = [msg]
            else:
                same_author = msg.is_bot == prev_msg.is_bot
                close_time = abs((msg.date - prev_msg.date).total_seconds()) < 300

                if same_author and close_time:
                    current_group.append(msg)
                else:
                    raw_groups.append(current_group)
                    current_group = [msg]
            prev_msg = msg

        if current_group:
            raw_groups.append(current_group)

        grouped_messages = [_build_group(g) for g in raw_groups]

        form = AdminReplyForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            text = form.cleaned_data["text"]

            async def send_message():
                async with Bot(settings.BOT_TOKEN) as bot:
                    return await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text
                    )

            sent_message = async_to_sync(send_message)()

            TgMessage.objects.create(
                message_id=sent_message.message_id,
                chat_id=user.telegram_id,
                user=user,
                text=text,
                is_bot=True,
                date=sent_message.date,
            )

            return redirect(request.path)

        context = {
            "user": user,
            "grouped_messages": grouped_messages,
            "form": form,
        }

        logger.info(f'Grouped messages count: {len(grouped_messages)}')

        return render(request, "admin/chat_view.html", context)