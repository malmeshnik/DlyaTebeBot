import secrets

from django.db import models
from django.conf import settings

message_help_text = """
Текст повідомлення може містити такі змінні:
{name} - ім'я користувача
{phone_number} - номер телефону користувача

Текст повідомлення може містити HTML-теги для форматування тексту.
Наприклад: <b>жирний текст</b>, <i>курсив</i>, <a href='https://example.com'>посилання</a>


Приклад тексту повідомлення:
Привіт, <b>{name}!</b>
Ваш номер телефону: <i>{phone_number}</i>.
Дякуємо, що користуєтесь нашим сервісом!
"""

# Create your models here.
class ViberUser(models.Model):
    viber_id = models.CharField(max_length=100, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Ім'я")
    phone_number = models.CharField(
        max_length=20, verbose_name="Номер телефону", null=True, blank=True
    )

    miniapp_token = models.CharField(
        max_length=255, verbose_name="Токен для miniapp", unique=True, default=secrets.token_urlsafe
    )

    is_subscribe = models.BooleanField(default=True, verbose_name="Підписаний")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Користувач Viber"
        verbose_name_plural = "Користувачі Viber"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class ViberMessage(models.Model):
    user = models.ForeignKey(
        ViberUser,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Користувач"
    )
    media_url = models.TextField(blank=True, null=True)
    text = models.TextField(verbose_name="Текст", null=True, blank=True)
    is_bot = models.BooleanField(default=False, verbose_name="Від бота")
    timestamp = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"{self.user.name}: {self.text[:50]}"

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        verbose_name = "Повідомлення Viber"
        verbose_name_plural = "Повідомлення Viber"
        ordering = ("created_at",)