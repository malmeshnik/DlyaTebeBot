from django.db import models


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