from django.contrib import admin

from .models import ViberUser, PromoCampaign, Message

@admin.register(ViberUser)
class ViberUserAdmin(admin.ModelAdmin):
    list_display = ("viber_id", "name", "phone_number")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")

@admin.register(PromoCampaign)
class PromoCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")