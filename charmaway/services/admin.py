from django.contrib import admin
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order_position', 'created_at']
    list_editable = ['order_position']
    search_fields = ['name', 'description']
    ordering = ['order_position', 'name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'offer_price', 'duration', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'is_available', 'is_featured']
    list_editable = ['is_available', 'is_featured']
    search_fields = ['name', 'description']
    ordering = ['-is_featured', 'name']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'category')
        }),
        ('Precio y Duración', {
            'fields': ('price', 'offer_price', 'duration')
        }),
        ('Imagen', {
            'fields': ('image',)
        }),
        ('Disponibilidad', {
            'fields': ('is_available', 'is_featured')
        }),
    )
