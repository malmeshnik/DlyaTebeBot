from django.apps import AppConfig


class BotConfig(AppConfig):
    """The application configuration for the `bot` app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        """Imports the signals when the app is ready."""
        from . import signals