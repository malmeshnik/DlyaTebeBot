from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    verbose_name = "Telegram Бот"
    verbose_name_plural = "Telegram Боти"

    def ready(self):
        from . import signals