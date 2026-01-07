from django.contrib import admin

from .models import ViberUser

@admin.register(ViberUser)
class ViberUserAdmin(admin.ModelAdmin):
    list_display = ("viber_id", "name", "phone_number")