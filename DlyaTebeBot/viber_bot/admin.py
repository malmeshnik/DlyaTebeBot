from django.contrib import admin
from django.db.models import Count, Q, Max
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django import forms
from django.conf import settings
from viberbot.api.messages import TextMessage
from unfold.admin import ModelAdmin, TabularInline

from .models import ViberUser, ViberMessage
from .views import viber
from .keyboards import main_menu

class ViberAdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

class ViberMessageInline(TabularInline):
    model = ViberMessage
    fields = ("text", "is_bot", "created_at")
    readonly_fields = ("text", "is_bot", "created_at")
    extra = 0
    can_delete = False

@admin.register(ViberUser)
class ViberUserAdmin(ModelAdmin):
    list_display = ("viber_id", "name", "phone_number", "unread_count", "created_at", "open_chat")
    search_fields = ("viber_id", "name", "phone_number")
    readonly_fields = ("viber_id", "created_at", "updated_at")
    inlines = [ViberMessageInline]

    def changelist_view(self, request, extra_context=None):
        # Підраховуємо загальну кількість непрочитаних
        total_unread = ViberUser.objects.aggregate(
            total=Count('messages', filter=Q(messages__is_read=False, messages__is_bot=False))
        )['total'] or 0

        extra_context = extra_context or {}
        extra_context['total_unread'] = total_unread
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            unread_total=Count("messages", filter=Q(messages__is_read=False, messages__is_bot=False)),
            last_message_date=Max("messages__created_at", filter=Q(messages__is_bot=False))
        )
        # Сортуємо за наявністю непрочитаних (більше = вище), потім за датою останнього повідомлення
        return queryset.order_by("-unread_total", "-last_message_date", "-created_at")

    def unread_count(self, obj):
        count = obj.unread_total
        if count > 0:
            return format_html(
                '<span style="display: inline-flex; align-items: center; justify-content: center; '
                'min-width: 24px; height: 24px; padding: 0 8px; background: rgb(115, 96, 242); '
                'color: white; border-radius: 12px; font-weight: 600; font-size: 0.75rem;">{}</span>',
                count
            )
        return "-"
    unread_count.short_description = "Непрочитані"

    def open_chat(self, obj):
        return format_html(
            '<a href="chat/{}/" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'padding: 0.5rem 1rem; background: rgb(115, 96, 242); color: white; '
            'border-radius: 0.5rem; text-decoration: none; font-weight: 500; '
            'font-size: 0.875rem; transition: background 0.2s; white-space: nowrap;" '
            'onmouseover="this.style.background=\'rgb(90, 73, 201)\'" '
            'onmouseout="this.style.background=\'rgb(115, 96, 242)\'">'
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
                name="viberuser-chat",
            ),
        ]
        return custom_urls + urls

    def chat_view(self, request, user_id):
        user = get_object_or_404(ViberUser, pk=user_id)
        messages = user.messages.all().order_by("created_at")

        # Позначаємо всі повідомлення від користувача як прочитані
        user.messages.filter(is_bot=False, is_read=False).update(is_read=True)

        form = ViberAdminReplyForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            text = form.cleaned_data["text"]

            # Send via Viber API
            viber.send_messages(user.viber_id, [TextMessage(text=text, keyboard=main_menu(user.viber_id), min_api_version=6)])

            # Save to database
            ViberMessage.objects.create(
                user=user,
                text=text,
                is_bot=True
            )

            return redirect(request.path)

        context = {
            **self.admin_site.each_context(request),
            "viber_user": user,
            "messages": messages,
            "form": form,
            "title": f"Viber чат з {user.name}",
            "site_title": self.admin_site.site_title,
            "site_header": self.admin_site.site_header,
            "has_permission": True,
            "opts": self.model._meta,
            "change": True,
            "is_popup": False,
            "save_as": False,
            "has_delete_permission": False,
            "has_add_permission": False,
            "has_change_permission": True,
            "has_view_permission": True,
        }

        return render(request, "admin/viber_chat_view.html", context)
