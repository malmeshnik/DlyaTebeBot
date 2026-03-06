from django.contrib import admin

from .models import Message, Button, PromoCampaign, BroadcastMessage


class ButtonInline(admin.TabularInline):
    model = Button
    extra = 1
    fields = ("text", "url", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("name", "description", "created_at", "updated_at")
    inlines = [ButtonInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(broadcastmessage__isnull=True)


@admin.register(PromoCampaign)
class PromoCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name",)


@admin.register(BroadcastMessage)
class BroadCastMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "scheduled_at",
        "send_in_tg",
        "send_in_viber",
    )
    
    inlines = [ButtonInline]
