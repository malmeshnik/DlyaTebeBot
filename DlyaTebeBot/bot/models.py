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

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = "Користувач Telegram"
        verbose_name_plural = "Користувачі Telegram"
