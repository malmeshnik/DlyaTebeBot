from django.db import models


# Create your models here.
class Message(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва повідомлення")
    image = models.ImageField(
        upload_to="media/messages/", blank=True, null=True, verbose_name="Зображення"
    )
    text = models.TextField(verbose_name="Текст повідомлення")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
