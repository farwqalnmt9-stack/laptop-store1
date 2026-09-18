import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Brand(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Use-case category: Gaming, Business, Student, Creator, Ultrabook..."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=10, blank=True, help_text='Emoji or short icon code')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Laptop(models.Model):
    STORAGE_TYPES = [
        ('SSD', 'SSD'),
        ('HDD', 'HDD'),
        ('HYBRID', 'SSD + HDD'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='laptops')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='laptops')

    # Specs
    cpu = models.CharField(max_length=100, help_text='e.g. Intel Core i7-13700H')
    cpu_cores = models.PositiveSmallIntegerField(default=8)
    ram_gb = models.PositiveSmallIntegerField(default=16)
    storage_gb = models.PositiveIntegerField(default=512)
    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPES, default='SSD')
    gpu = models.CharField(max_length=100, help_text='e.g. NVIDIA RTX 4060')
    screen_size = models.DecimalField(max_digits=4, decimal_places=1, default=15.6)
    resolution = models.CharField(max_length=30, default='1920x1080')
    refresh_rate = models.PositiveSmallIntegerField(default=60, help_text='Hz')
    battery_wh = models.PositiveSmallIntegerField(default=60, help_text='Watt-hour')
    weight_kg = models.DecimalField(max_digits=4, decimal_places=2, default=1.8)
    os = models.CharField(max_length=50, default='Windows 11')

    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=30, unique=True, blank=True)

    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='laptops/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='laptops/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='laptops/', blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Laptop.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base_slug}-{n}'
            self.slug = slug
        if not self.sku:
            self.sku = f'LT-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(agg, 1) if agg else 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def spec_tags(self):
        """Short spec chips used on cards, e.g. ['Core i7', '16GB', '512GB SSD']"""
        return [self.cpu, f'{self.ram_gb}GB RAM', f'{self.storage_gb}GB {self.storage_type}', self.gpu]


class Review(models.Model):
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['laptop', 'user']

    def __str__(self):
        return f'{self.laptop.name} - {self.rating} stars by {self.user}'


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'laptop']
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user} <3 {self.laptop.name}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} - {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    laptop = models.ForeignKey(Laptop, on_delete=models.SET_NULL, null=True)
    laptop_name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.laptop_name} x{self.quantity}'
