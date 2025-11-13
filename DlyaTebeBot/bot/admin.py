from django.contrib import admin

from .models import Message, TgUser, Button, PromoCampaign


class ButtonInline(admin.TabularInline):
    """An inline admin descriptor for the `Button` model."""
    model = Button
    extra = 1
    fields = ("text", "url", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """The admin model for the `Message` model."""
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    inlines = [ButtonInline]


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    """The admin model for the `TgUser` model."""
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
    """The admin model for the `PromoCampaign` model."""
    list_display = (
        "name",
        "start_date",
        "end_date"
    )
    search_fields = ("name",)
    