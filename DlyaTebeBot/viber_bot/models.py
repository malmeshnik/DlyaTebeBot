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

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Користувач Viber"
        verbose_name_plural = "Користувачі Viber"

class Message(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва повідомлення")
    text = models.TextField(verbose_name="Текст повідомлення", help_text=message_help_text)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

class PromoCampaign(models.Model):
    name = models.CharField(verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    image = models.ImageField(upload_to="promocampaign/", verbose_name="Фото")
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