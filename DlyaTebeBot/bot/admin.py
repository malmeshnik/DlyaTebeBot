from aiogram import Bot
from loguru import logger

from django.contrib import admin
from django.db.models import Count, Q, Max
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django import forms
from django.conf import settings
from asgiref.sync import async_to_sync
from unfold.admin import ModelAdmin, TabularInline
from .models import TgUser, TgMessage

class AdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)


class TgMessageInline(TabularInline):
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
class TgUserAdmin(ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "full_name",
        "phone_number",
        "is_admin",
        "unread_count",
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

    inlines = [TgMessageInline]

    def changelist_view(self, request, extra_context=None):
        # Підраховуємо загальну кількість непрочитаних
        from django.db.models import Count, Q
        total_unread = TgUser.objects.aggregate(
            total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
        )['total'] or 0

        extra_context = extra_context or {}
        extra_context['total_unread'] = total_unread
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            messages_total=Count("messages"),
            unread_total=Count("messages", filter=Q(messages__is_read=False, messages__is_bot=False)),
            last_message_date=Max("messages__date", filter=Q(messages__is_bot=False))
        )
        # Примусово скидаємо інші сортування через .order_by() і ставимо наше
        return queryset.order_by("-unread_total", "-last_message_date")

    def full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
    full_name.short_description = "Повне ім'я"

    def unread_count(self, obj):
        count = obj.unread_total
        if count > 0:
            return format_html(
                '<span style="display: inline-flex; align-items: center; justify-content: center; '
                'min-width: 24px; height: 24px; padding: 0 8px; background: rgb(239, 68, 68); '
                'color: white; border-radius: 12px; font-weight: 600; font-size: 0.75rem;">{}</span>',
                count
            )
        return "-"
    unread_count.short_description = "Непрочитані"

    def messages_count(self, obj):
        return obj.messages_total
    messages_count.short_description = "К-сть повідомлень"

    def open_chat(self, obj):
        return format_html(
            '<a href="chat/{}/" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'padding: 0.5rem 1rem; background: rgb(59, 130, 246); color: white; '
            'border-radius: 0.5rem; text-decoration: none; font-weight: 500; '
            'font-size: 0.875rem; transition: background 0.2s; white-space: nowrap;" '
            'onmouseover="this.style.background=\'rgb(37, 99, 235)\'" '
            'onmouseout="this.style.background=\'rgb(59, 130, 246)\'">'
            '💬 Відкрити чат</a>',
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

        # Позначаємо всі повідомлення від користувача як прочитані
        user.messages.filter(is_bot=False, is_read=False).update(is_read=True)

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
            **self.admin_site.each_context(request),
            "tg_user": user,
            "grouped_messages": grouped_messages,
            "form": form,
            "title": f"Чат з {user.first_name or user.username}",
            "site_title": self.admin_site.site_title,
            "site_header": self.admin_site.site_header,
            "has_permission": True,
        }

        logger.info(f'Grouped messages count: {len(grouped_messages)}')

        return render(request, "admin/chat_view.html", context)