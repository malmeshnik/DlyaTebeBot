from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html

help_text_msg = format_html(
    """
    Для форматування повідомлення використайте теги:<br><br>
    {}<br>
    {}<br>
    {}<br><br>
    Щоб вставити змінні використайте:<br>
    {}<br>
    {}<br>
    """,
    format_html("&lt;b&gt;<b>{}</b>&lt;/b&gt;", "Жирний текст"),
    format_html("&lt;i&gt;<i>{}</i>&lt;/i&gt;", "Курсив"),
    format_html(
        '&lt;a href="https://theandriy.xyz/"&gt;<a href="https://theandriy.xyz/">{}</a>&lt;/a&gt;',
        "Клікабельний текст",
    ),
    "{bonus} = Кількість бонусів користувача",
    "{name} = Ім'я користувача",
)

class Message(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва повідомлення")
    image = models.ImageField(
        upload_to="messages/", blank=True, null=True, verbose_name="Зображення"
    )
    text = models.TextField(
        max_length=4096, verbose_name="Текст повідомлення", help_text=help_text_msg
    )

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
        related_name="buttons",
        verbose_name="Повідомлення",
    )
    text = models.CharField(max_length=60, verbose_name="Текст кнопки")
    url = models.URLField(max_length=250, verbose_name="URL кнопки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Кнопка"
        verbose_name_plural = "Кнопки"

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

class BroadcastMessage(Message):
    scheduled_at = models.DateTimeField(
        verbose_name="Дата та час відправки повідомлення",
        blank=True,
        null=True,
        help_text="Якщо не вказати буде відправлено відразу",
    )
    send = models.BooleanField(default=False, verbose_name="Відправлено")

    def __str__(self):
        return self.name
    
    def save(self):
        if not self.scheduled_at:
            self.scheduled_at = timezone.now()
        super().save()

    class Meta:
        verbose_name = "Розсилка"
        verbose_name_plural = "Розсилки"