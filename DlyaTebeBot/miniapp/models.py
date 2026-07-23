from django.db import models
from django.utils.text import slugify
import secrets


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


class WheelPrize(models.Model):
    """Приз колеса фортуни"""

    COLOR_CHOICES = [
        ('#ffcce0', 'Рожевий'),        # h=350, s=42 - ніжний рожевий
        ('#ffe0c2', 'Персиковий'),     # h=28, s=45 - м'який персик
        ('#fff0c8', 'Жовтий'),         # h=40, s=38 - пастельний жовтий
        ('#d4ecd4', 'М\'ятний'),       # h=95, s=28 - світлий м'ятний
        ('#d4ece4', 'Бірюзовий'),      # h=150, s=28 - ніжна бірюза
        ('#d8e4f0', 'Блакитний'),      # h=220, s=26 - пастельний блакитний
        ('#e4d8f0', 'Лавандовий'),     # h=268, s=34 - м'яка лаванда
        ('#f0e0ec', 'Рожево-ліловий'), # h=300, s=30 - пудровий
        ('#ffe8d0', 'Абрикосовий'),    # h=35, s=40 - світлий абрикос
        ('#fffce0', 'Кремовий'),       # h=50, s=35 - ніжний крем
        ('#e0f0d8', 'Світло-зелений'), # h=100, s=30 - пастельний зелений
        ('#d8f0ec', 'Аквамариновий'),  # h=160, s=28 - легка аква
        ('#e0e8fc', 'Перлинний синій'),# h=230, s=28 - перлинний
        ('#ecd8f8', 'Фіолетовий'),     # h=280, s=32 - світлий фіолет
        ('#ffd8e8', 'Коралловий'),     # h=340, s=38 - ніжний корал
    ]

    name = models.CharField(max_length=100, verbose_name="Назва призу")

    win_image = models.ImageField(
        upload_to="wheel_prizes/win_images/",
        verbose_name="Фото виграшу",
        help_text="Фото, яке користувач бачить після виграшу цього призу",
        blank=True,
        null=True
    )
    message_text = models.TextField(
        verbose_name="Текст повідомлення",
        help_text="Текст, який користувач бачить після виграшу цього призу"
    )
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ймовірність (%)",
        help_text="Шанс випадіння від 0 до 100"
    )
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#FFB5D8',
        verbose_name="Колір сектора"
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Порядок на колесі",
        help_text="Позиція сектора на колесі (0-N)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний"
    )
    lose = models.BooleanField(
        default=False,
        verbose_name="Приз-програш",
        help_text="Позначте, якщо цей приз є програшем (користувач нічого не виграв)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.probability}%)"

    class Meta:
        verbose_name = "Приз колеса фортуни"
        verbose_name_plural = "Призи колеса фортуни"
        ordering = ['sort_order', 'id']


class WheelSpin(models.Model):
    """Історія прокрутів колеса фортуни"""

    code = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Код виграшу",
        editable=False
    )
    prize = models.ForeignKey(
        WheelPrize,
        on_delete=models.CASCADE,
        related_name="spins",
        verbose_name="Приз"
    )
    tg_user = models.ForeignKey(
        "bot.TgUser",
        on_delete=models.CASCADE,
        related_name="wheel_spins",
        verbose_name="Телеграм користувач",
        null=True,
        blank=True
    )
    viber_user = models.ForeignKey(
        "viber_bot.ViberUser",
        on_delete=models.CASCADE,
        related_name="wheel_spins",
        verbose_name="Вайбер користувач",
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Ключ сесії",
        help_text="Для анонімних користувачів"
    )
    is_claimed = models.BooleanField(
        default=False,
        verbose_name="Приз забрано"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата прокруту"
    )
    claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата активації"
    )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        """Генерує унікальний код виграшу"""
        while True:
            code = f"W{secrets.token_urlsafe(8)}"
            if not WheelSpin.objects.filter(code=code).exists():
                return code

    @property
    def user(self):
        return self.tg_user if self.tg_user else self.viber_user

    @property
    def platform(self):
        if self.tg_user:
            return "Telegram"
        elif self.viber_user:
            return "Viber"
        return "Анонімний"

    def __str__(self):
        user_str = str(self.user) if self.user else "Анонімний"
        return f"{user_str} - {self.prize.name} ({self.code})"

    class Meta:
        verbose_name = "Прокрут колеса"
        verbose_name_plural = "Прокрути колеса"
        ordering = ['-created_at']