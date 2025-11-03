from django.contrib import admin

from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")