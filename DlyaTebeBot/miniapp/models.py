from django.db import models
from django.utils.text import slugify


class Gender(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to="gender/", blank=True, null=True, verbose_name="Фото"
    )
    description = models.TextField(blank=True, verbose_name="Опис")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Для кого"
        verbose_name_plural = "Для кого"


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(unique=True, blank=True)
    gender = models.ForeignKey(
        Gender,
        related_name="brands",
        on_delete=models.CASCADE,
        verbose_name="Для кого",
    )

    image = models.ImageField(
        upload_to="brands/", verbose_name="Фото", blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренди"


class Product(models.Model):

    gender = models.ForeignKey(
        Gender,
        related_name="products",
        verbose_name="Для кого",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="products/", verbose_name="Фото")
    brand = models.ForeignKey(
        Brand,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Бренд",
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна до скидки",
    )
    characteristics = models.TextField(verbose_name="Опис")
    is_available = models.BooleanField(default=True, verbose_name="В наявності")
    available = models.IntegerField(default=999, verbose_name="Доступно")
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Порядок відображення"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="Створено"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name="Продукт",
        related_name="variants"
    )
    volume_ml = models.PositiveIntegerField(verbose_name="Кількість мл.")
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна')
    old_price = models.DecimalField(
        decimal_places=2, 
        max_digits=10,
        blank=True,
        null=True,
        verbose_name="Ціна до скидки"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} {self.volume_ml} ML"

    class Meta:
        verbose_name = "Варіант продукту"
        verbose_name_plural = "Варіанти продуктів"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="gallery",
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Фото")

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = "Фото продукта"
        verbose_name_plural = "Фото продуктов"

class Banner(models.Model):
    image = models.ImageField(upload_to="products/banners/", verbose_name="Фото")
    link = models.URLField(blank=True, null=True, verbose_name="Посилання")

    def __str__(self):
        return self.image.path
    
    class Meta:
        verbose_name = "Банер"
        verbose_name_plural = "Банери"

class Order(models.Model):
    STATUS_CHOICES = (
        ("new", "Нове"),
        ("in_progress", "В роботі"),
        ("done", "Завершено"),
        ("canceled", "Скасовано"),
    )
    tg_user = models.ForeignKey(
        "bot.TgUser",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Телеграм користувач",
        null=True,
        blank=True
    )

    viber_user = models.ForeignKey(
        "viber_bot.ViberUser",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Вайбер користувач",
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Продукт"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Варіант"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус"
    )

    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"
    
    @property
    def order_name(self):
        return f"Замовлення #{self.id}"
    
    @property
    def user(self):
        return self.tg_user if self.tg_user else self.viber_user

    @property
    def platform(self):
        return "Viber" if self.viber_user else "Telegram"
    
    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"