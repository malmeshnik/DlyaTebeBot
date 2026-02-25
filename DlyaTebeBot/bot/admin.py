from django.contrib import admin
from .models import TgUser

@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "is_admin",
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