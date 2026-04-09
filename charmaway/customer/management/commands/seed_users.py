from django.core.management.base import BaseCommand
from customer.models import Customer

class Command(BaseCommand):
    help = 'Crea un admin y un usuario normal de prueba'

    def handle(self, *args, **options):
        if not Customer.objects.filter(email='admin@example.com').exists():
            Customer.objects.create_superuser(
                email='admin@example.com',
                password='SecurePassword',
                name='Wade',
                surnames='Wilson',
                phone='+34123456789',
                address='Calle Admin 1',
                city='Nueva York',
                zip_code='00000'
            )
            self.stdout.write(self.style.SUCCESS('Admin creado correctamente'))

        if not Customer.objects.filter(email='user@example.com').exists():
            Customer.objects.create_user(
                email='user@example.com',
                password='SecurePassword',
                name='Peter',
                surnames='Parker',
                phone='+34111222333',
                address='Ingram Street 20',
                city='Nueva York',
                zip_code='00000'
            )
            self.stdout.write(self.style.SUCCESS('Usuario normal creado correctamente'))

        if not Customer.objects.filter(email='customer1@example.com').exists():
            Customer.objects.create_user(
                email='customer1@example.com',
                password='CustomerPassword',
                name='Customer',
                surnames='Uno',
                phone='+34666000001',
                address='Calle Mayor 10',
                city='Madrid',
                zip_code='28001'
            )
            self.stdout.write(self.style.SUCCESS('Customer 1 creado correctamente'))

        if not Customer.objects.filter(email='customer2@example.com').exists():
            Customer.objects.create_user(
                email='customer2@example.com',
                password='CustomerPassword',
                name='Customer',
                surnames='Dos',
                phone='+34666000002',
                address='Avenida Reina Mercedes 124',
                city='Sevilla',
                zip_code='41012'
            )
            self.stdout.write(self.style.SUCCESS('Customer 2 creado correctamente'))

        if not Customer.objects.filter(email='customer3@example.com').exists():
            Customer.objects.create_user(
                email='customer3@example.com',
                password='CustomerPassword',
                name='Customer',
                surnames='Tres',
                phone='+34666000003',
                address='Paseo de la Luna 15',
                city='Barcelona',
                zip_code='08001'
            )
            self.stdout.write(self.style.SUCCESS('Customer 3 creado correctamente'))

        if not Customer.objects.filter(email='customer4@example.com').exists():
            Customer.objects.create_user(
                email='customer4@example.com',
                password='CustomerPassword',
                name='Customer',
                surnames='Cuatro',
                phone='+34666000004',
                address='Ronda del Río 22',
                city='Valencia',
                zip_code='46001'
            )
            self.stdout.write(self.style.SUCCESS('Customer 4 creado correctamente'))

        if not Customer.objects.filter(email='customer5@example.com').exists():
            Customer.objects.create_user(
                email='customer5@example.com',
                password='CustomerPassword',
                name='Customer',
                surnames='Cinco',
                phone='+34666000005',
                address='Calle del Sol 99',
                city='Bilbao',
                zip_code='48001'
            )
            self.stdout.write(self.style.SUCCESS('Customer 5 creado correctamente'))
