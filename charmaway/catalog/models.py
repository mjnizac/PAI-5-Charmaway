from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)
    order_position = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order_position', 'name']


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='categories', null=True, blank=True)
    order_position = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order_position', 'name']


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    @property
    def has_offer(self):
        return self.offer_price is not None and self.offer_price < self.price

    @property
    def final_price(self):
        return self.offer_price if self.has_offer else self.price

    @property
    def discount_percentage(self):
        if self.has_offer:
            return round(((self.price - self.offer_price) / self.price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.CharField(max_length=255)
    is_main = models.BooleanField(default=False)
    order_position = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Image {self.order_position}"

    class Meta:
        ordering = ['order_position']


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10, default="Estándar")
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    class Meta:
        unique_together = ('product', 'size')
        ordering = ['size']