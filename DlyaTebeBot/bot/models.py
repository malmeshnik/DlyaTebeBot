from django.db import models
from django.conf import settings


# Create your models here.
class Message(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва повідомлення")
    image = models.ImageField(
        upload_to="messages/", blank=True, null=True, verbose_name="Зображення"
    )
    text = models.TextField(max_length=4096, verbose_name="Текст повідомлення")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

class Button(models.Model):
    message = models.ForeignKey(
            Message, 
            on_delete=models.CASCADE, 
            related_name='buttons',
            verbose_name="Повідомлення",
        )
    text = models.CharField(max_length=60, verbose_name="Текст кнопки")
    url = models.URLField(
            max_length=250, 
            verbose_name="URL кнопки"
        )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = "Кнопка"
        verbose_name_plural = "Кнопки"


class TgUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=100, 
        verbose_name="Юзернейм",
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=20, 
        verbose_name="Номер телефону", 
        null=True, 
        blank=True
    )
    first_name = models.CharField(
        max_length=100, 
        verbose_name="Ім'я", 
        null=True, 
        blank=True
    )
    last_name = models.CharField(
        max_length=100, 
        verbose_name="Прізвище",
        null=True,
        blank=True
    )

    main_message_id = models.BigIntegerField(
        verbose_name="ID повідомлення з головним меню",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.first_name
    
    class Meta:
        verbose_name = "Користувач Telegram"
        verbose_name_plural = "Користувачі Telegram"

class PromoCampaign(models.Model):
    name = models.CharField(verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    image = models.ImageField(upload_to="promocampaign/")
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(verbose_name="Дата завершення")

    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        return settings.DOMAIN + self.image.url
    
    class Meta:
        verbose_name = "Акція"
        verbose_name_plural = "Акції"