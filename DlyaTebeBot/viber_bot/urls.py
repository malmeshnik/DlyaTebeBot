from django.urls import path

from .views import viber_webhook

urlpatterns = [
    path("webhook/", viber_webhook, name="viber_webhook"),
]
