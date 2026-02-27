from django.db import models


class TgUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=100, verbose_name="Юзернейм", null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=20, verbose_name="Номер телефону", null=True, blank=True
    )
    first_name = models.CharField(
        max_length=100, verbose_name="Ім'я", null=True, blank=True
    )
    last_name = models.CharField(
        max_length=100, verbose_name="Прізвище", null=True, blank=True
    )

    main_message_id = models.BigIntegerField(
        verbose_name="ID повідомлення з головним меню", null=True, blank=True
    )

    is_admin = models.BooleanField(default=False, verbose_name="Адмін")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = "Користувач Telegram"
        verbose_name_plural = "Користувачі Telegram"

class TgMessage(models.Model):
    message_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=50)

    user = models.ForeignKey(
        TgUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages"
    )

    text = models.TextField(null=True, blank=True)
    caption = models.TextField(null=True, blank=True)

    is_bot = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    edit_date = models.DateTimeField(null=True, blank=True)

    date = models.DateTimeField()
    raw_data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message_id", "chat_id")
        indexes = [
            models.Index(fields=["chat_id"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.chat_id} | {self.message_id}"
    
class TgMessageMedia(models.Model):
    MEDIA_TYPES = [
        ("photo", "Photo"),
        ("video", "Video"),
        ("document", "Document"),
        ("audio", "Audio"),
        ("voice", "Voice"),
        ("sticker", "Sticker"),
        ("animation", "Animation"),
    ]

    message = models.ForeignKey(
        TgMessage,
        on_delete=models.CASCADE,
        related_name="media"
    )

    file_id = models.CharField(max_length=512)
    file_unique_id = models.CharField(max_length=512)
    file_type = models.CharField(max_length=20, choices=MEDIA_TYPES)

    file_path = models.CharField(max_length=1024, null=True, blank=True)
    file_url = models.URLField(null=True, blank=True)

    file_name = models.CharField(max_length=255, null=True, blank=True)
    mime_type = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} | {self.file_id}"
    
class TgMessageReaction(models.Model):
    message = models.ForeignKey(
        TgMessage,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    user = models.ForeignKey(
        TgUser,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    emoji = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user", "emoji")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["message"]),
        ]

    def __str__(self):
        return f"{self.user.telegram_id} → {self.emoji}"