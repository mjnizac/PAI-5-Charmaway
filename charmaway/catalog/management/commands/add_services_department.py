from django.core.management.base import BaseCommand
from catalog.models import Department, Category


class Command(BaseCommand):
    help = 'Add Services department and its categories to the existing catalog'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding Services department...')

        # Check if Services department already exists
        services_dept, created = Department.objects.get_or_create(
            name='Servicios',
            defaults={
                'order_position': 8,
                'description': 'Servicios de belleza, asesoramiento y entrega',
                'image': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=400&q=80'
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Services department'))
        else:
            self.stdout.write(self.style.WARNING(f'Services department already exists'))

        # Create Service Categories
        self.stdout.write('Adding service categories...')
        categories_data = [
            {'name': 'Asesoramiento y Consultoría', 'description': 'Servicios de asesoramiento personalizado', 'department': services_dept, 'order_position': 1},
            {'name': 'Tutoriales y Masterclass', 'description': 'Clases y tutoriales de maquillaje', 'department': services_dept, 'order_position': 2},
            {'name': 'Servicios de Entrega', 'description': 'Opciones de envío y empaquetado', 'department': services_dept, 'order_position': 3},
            {'name': 'Personalización', 'description': 'Servicios de personalización de productos', 'department': services_dept, 'order_position': 4},
            {'name': 'Suscripciones', 'description': 'Cajas y membresías mensuales', 'department': services_dept, 'order_position': 5},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                department=services_dept,
                defaults={
                    'description': cat_data['description'],
                    'order_position': cat_data['order_position']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))

        self.stdout.write(self.style.SUCCESS('Services department setup completed!'))
