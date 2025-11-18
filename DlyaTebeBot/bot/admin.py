from django.contrib import admin

from .models import Message, TgUser, Button, PromoCampaign, BroadcastMessage


class ButtonInline(admin.TabularInline):
    model = Button
    extra = 1
    fields = ("text", "url", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    inlines = [ButtonInline]


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "phone_number",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(PromoCampaign)
class PromoCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date"
    )
    search_fields = ("name",)
    

@admin.register(BroadcastMessage)
class BroadCastMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "scheduled_at", "send",)
    inlines = [ButtonInline]