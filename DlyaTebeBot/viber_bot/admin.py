from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django import forms
from django.conf import settings
from viberbot.api.messages import TextMessage

from .models import ViberUser, ViberMessage
from .views import viber

class ViberAdminReplyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

class ViberMessageInline(admin.TabularInline):
    model = ViberMessage
    fields = ("text", "is_bot", "created_at")
    readonly_fields = ("text", "is_bot", "created_at")
    extra = 0
    can_delete = False

@admin.register(ViberUser)
class ViberUserAdmin(admin.ModelAdmin):
    list_display = ("viber_id", "name", "phone_number", "created_at", "open_chat")
    search_fields = ("viber_id", "name", "phone_number")
    readonly_fields = ("viber_id", "created_at", "updated_at")
    inlines = [ViberMessageInline]

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
                name="viberuser-chat",
            ),
        ]
        return custom_urls + urls

    def chat_view(self, request, user_id):
        user = get_object_or_404(ViberUser, pk=user_id)
        messages = user.messages.all().order_by("created_at")

        form = ViberAdminReplyForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            text = form.cleaned_data["text"]

            # Send via Viber API
            viber.send_messages(user.viber_id, [TextMessage(text=text)])

            # Save to database
            ViberMessage.objects.create(
                user=user,
                text=text,
                is_bot=True
            )

            return redirect(request.path)

        context = {
            "user": user,
            "messages": messages,
            "form": form,
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

@admin.register(ViberMessage)
class ViberMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "is_bot", "created_at")
    list_filter = ("is_bot", "created_at")
    search_fields = ("text", "user__name", "user__viber_id")
