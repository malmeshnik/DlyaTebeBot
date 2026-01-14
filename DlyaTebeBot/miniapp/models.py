from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назване")
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, verbose_name="Фото"
    )
    description = models.TextField(blank=True, verbose_name="Описание")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назване")
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        related_name="brands",
        on_delete=models.CASCADE,
        verbose_name="Категория",
    )

    image = models.ImageField(
        upload_to="brands/", verbose_name="Фото", blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

class Model(models.Model):
    name = models.CharField(max_length=255, verbose_name="Модель")
    slug = models.SlugField(unique=True)
    brand = models.ForeignKey(
        Brand,
        related_name="models",
        on_delete=models.CASCADE,
        verbose_name="Бренд"
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Модель продукта"
        verbose_name_plural = "Модели продуктов"
        ordering = ["name"]


class Product(models.Model):

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        verbose_name="Категории",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, verbose_name="Назване")
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

    model = models.ForeignKey(
        Model,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Модель"
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Цена до скидки",
    )
    characteristics = models.TextField(verbose_name="Характеристики")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    available = models.IntegerField(default=999, verbose_name="Доступно")
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="Создано"
    )
    popularity = models.IntegerField(default=0, verbose_name="Популярность")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


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
    link = models.URLField(blank=True, null=True, verbose_name="Ссылка")

    def __str__(self):
        return self.image.path
    
    class Meta:
        verbose_name = "Банер"
        verbose_name_plural = "Банеры"