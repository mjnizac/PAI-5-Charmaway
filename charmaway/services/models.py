from django.db import models
from catalog.models import Category


class ServiceCategory(models.Model):
    """Categories for services"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['order_position', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Services that can be added to cart"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='services', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 30 minutos, 1 hora")
    image = models.URLField(max_length=500)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    def get_final_price(self):
        """Return offer price if available, otherwise regular price"""
        return self.offer_price if self.offer_price else self.price
