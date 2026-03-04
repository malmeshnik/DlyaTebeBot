from aiogram import Bot
from loguru import logger

from django.contrib import admin
from django.db.models import Count
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django import forms
from django.conf import settings
from asgiref.sync import async_to_sync
from .models import TgUser, TgMessage


class AdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)


class TgMessageInline(admin.TabularInline):
    model = TgMessage
    fields = ("message_id", "chat_id", "text", "date", "is_edited")
    readonly_fields = ("message_id", "chat_id", "text", "date", "is_edited")
    extra = 0
    show_change_link = True
    ordering = ("-date",)


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

    # Caption: збираємо з медіа або з повідомлень
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


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "full_name",
        "phone_number",
        "is_admin",
        "messages_count",
        "created_at",
        "open_chat",
    )

    list_filter = (
        "is_admin",
        "created_at",
    )

    search_fields = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "phone_number",
    )

    readonly_fields = (
        "telegram_id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = [TgMessageInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(messages_total=Count("messages"))

    def full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
    full_name.short_description = "Повне ім'я"

    def messages_count(self, obj):
        return obj.messages_total
    messages_count.short_description = "К-сть повідомлень"

    def open_chat(self, obj):
        return format_html(
            '<a class="button" href="chat/{}/">Відкрити чат</a>',
            obj.id
        )
    open_chat.short_description = "Чат"

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