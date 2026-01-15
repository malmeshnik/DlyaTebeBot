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
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
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