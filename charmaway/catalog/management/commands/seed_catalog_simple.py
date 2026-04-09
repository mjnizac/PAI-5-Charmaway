from django.core.management.base import BaseCommand
from catalog.models import Department, Brand, Category, Product, ProductImage, ProductSize
from order.models import Order
import random


class Command(BaseCommand):
    help = 'Seed the database with cosmetic products data (simplified version)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting catalog seeding (simplified)...')

        # Clear existing data
        Order.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductSize.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Department.objects.all().delete()

        # Create Departments (9 departments: 7 product departments + 3 service departments)
        self.stdout.write('Creating departments...')
        departments_data = [
            {'name': 'Maquillaje', 'order_position': 1, 'description': 'Productos de maquillaje para ojos, labios y rostro', 'image': 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Cuidado Facial', 'order_position': 2, 'description': 'Productos para el cuidado y tratamiento facial', 'image': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Cuidado Corporal', 'order_position': 3, 'description': 'Productos para el cuidado del cuerpo', 'image': 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Cuidado del Cabello', 'order_position': 4, 'description': 'Productos para el cuidado y tratamiento capilar', 'image': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Fragancias', 'order_position': 5, 'description': 'Perfumes y fragancias para hombre y mujer', 'image': 'https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Cuidado de Uñas', 'order_position': 6, 'description': 'Esmaltes y productos para el cuidado de uñas', 'image': 'https://images.unsplash.com/photo-1610992015732-2449b76344bc?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Accesorios y Herramientas', 'order_position': 7, 'description': 'Brochas, esponjas, herramientas y accesorios de belleza', 'image': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=400&q=80'},
            # Service Departments
            {'name': 'Beauty Academy', 'order_position': 8, 'description': 'Formación y asesoramiento personalizado', 'image': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Premium Services', 'order_position': 9, 'description': 'Servicios de entrega y personalización exclusivos', 'image': 'https://images.unsplash.com/photo-1607083206968-13611e3d76db?auto=format&fit=crop&w=400&q=80'},
            {'name': 'Club Exclusivo', 'order_position': 10, 'description': 'Membresías y suscripciones VIP', 'image': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=400&q=80'},
        ]

        departments = {}
        for dept_data in departments_data:
            dept = Department.objects.create(**dept_data)
            departments[dept.name] = dept
            self.stdout.write(f'Created department: {dept.name}')

        # Create Brands
        self.stdout.write('Creating brands...')
        brands_data = [
            'L\'Oréal Paris', 'Maybelline', 'Garnier', 'Nivea', 'The Ordinary',
            'CeraVe', 'NYX Professional Makeup', 'Neutrogena', 'Revlon', 'La Roche-Posay',
            'Vichy', 'Clinique', 'MAC Cosmetics', 'Estée Lauder', 'Lancôme',
            'Benefit Cosmetics', 'Urban Decay', 'Kiehl\'s', 'The Body Shop', 'Bioderma',
            'Nuxe', 'Rimmel London', 'Dove', 'Olay', 'Catrice'
        ]

        brands = {}
        for brand_name in brands_data:
            brand = Brand.objects.create(name=brand_name, description=f'Productos de {brand_name}')
            brands[brand_name] = brand
            self.stdout.write(f'Created brand: {brand_name}')

        # Create Categories - 50 categorías según especificación
        self.stdout.write('Creating categories...')
        categories_data = [
            # Departamento 1: MAQUILLAJE (10 categorías)
            {'name': 'Bases y correctores', 'description': 'Bases de maquillaje y correctores', 'department': departments['Maquillaje'], 'order_position': 1},
            {'name': 'Polvos', 'description': 'Polvos compactos y sueltos', 'department': departments['Maquillaje'], 'order_position': 2},
            {'name': 'Coloretes y bronceadores', 'description': 'Coloretes y bronceadores para el rostro', 'department': departments['Maquillaje'], 'order_position': 3},
            {'name': 'Iluminadores', 'description': 'Iluminadores y highlighters', 'department': departments['Maquillaje'], 'order_position': 4},
            {'name': 'Sombras de ojos', 'description': 'Paletas y sombras de ojos', 'department': departments['Maquillaje'], 'order_position': 5},
            {'name': 'Delineadores y lápices de ojos', 'description': 'Delineadores y lápices para ojos', 'department': departments['Maquillaje'], 'order_position': 6},
            {'name': 'Máscaras de pestañas', 'description': 'Máscaras de pestañas', 'department': departments['Maquillaje'], 'order_position': 7},
            {'name': 'Labiales', 'description': 'Barras de labios y lápices labiales', 'department': departments['Maquillaje'], 'order_position': 8},
            {'name': 'Gloss labial', 'description': 'Brillos y gloss para labios', 'department': departments['Maquillaje'], 'order_position': 9},
            {'name': 'Brochas y esponjas', 'description': 'Brochas y esponjas de maquillaje', 'department': departments['Maquillaje'], 'order_position': 10},

            # Departamento 2: CUIDADO FACIAL (8 categorías)
            {'name': 'Limpiadores faciales', 'description': 'Limpiadores y desmaquillantes faciales', 'department': departments['Cuidado Facial'], 'order_position': 1},
            {'name': 'Tónicos', 'description': 'Tónicos faciales', 'department': departments['Cuidado Facial'], 'order_position': 2},
            {'name': 'Serums', 'description': 'Serums y tratamientos concentrados', 'department': departments['Cuidado Facial'], 'order_position': 3},
            {'name': 'Contornos de ojos', 'description': 'Cremas y tratamientos para contorno de ojos', 'department': departments['Cuidado Facial'], 'order_position': 4},
            {'name': 'Hidratantes faciales', 'description': 'Cremas hidratantes faciales', 'department': departments['Cuidado Facial'], 'order_position': 5},
            {'name': 'Mascarillas faciales', 'description': 'Mascarillas y tratamientos faciales', 'department': departments['Cuidado Facial'], 'order_position': 6},
            {'name': 'Exfoliantes faciales', 'description': 'Exfoliantes y peelings faciales', 'department': departments['Cuidado Facial'], 'order_position': 7},
            {'name': 'Protectores solares faciales', 'description': 'Protección solar facial', 'department': departments['Cuidado Facial'], 'order_position': 8},

            # Departamento 3: CUIDADO CORPORAL (8 categorías)
            {'name': 'Geles y jabones corporales', 'description': 'Geles de ducha y jabones corporales', 'department': departments['Cuidado Corporal'], 'order_position': 1},
            {'name': 'Hidratantes corporales', 'description': 'Cremas y lociones hidratantes corporales', 'department': departments['Cuidado Corporal'], 'order_position': 2},
            {'name': 'Exfoliantes corporales', 'description': 'Exfoliantes y scrubs corporales', 'department': departments['Cuidado Corporal'], 'order_position': 3},
            {'name': 'Aceites corporales', 'description': 'Aceites hidratantes corporales', 'department': departments['Cuidado Corporal'], 'order_position': 4},
            {'name': 'Protectores solares corporales', 'description': 'Protección solar corporal', 'department': departments['Cuidado Corporal'], 'order_position': 5},
            {'name': 'Desodorantes', 'description': 'Desodorantes y antitranspirantes', 'department': departments['Cuidado Corporal'], 'order_position': 6},
            {'name': 'Cuidado de manos', 'description': 'Cremas y tratamientos para manos', 'department': departments['Cuidado Corporal'], 'order_position': 7},
            {'name': 'Cuidado de pies', 'description': 'Cremas y tratamientos para pies', 'department': departments['Cuidado Corporal'], 'order_position': 8},

            # Departamento 4: CUIDADO DEL CABELLO (7 categorías)
            {'name': 'Champús', 'description': 'Champús para todo tipo de cabello', 'department': departments['Cuidado del Cabello'], 'order_position': 1},
            {'name': 'Acondicionadores', 'description': 'Acondicionadores para el cabello', 'department': departments['Cuidado del Cabello'], 'order_position': 2},
            {'name': 'Mascarillas capilares', 'description': 'Mascarillas y tratamientos intensivos', 'department': departments['Cuidado del Cabello'], 'order_position': 3},
            {'name': 'Tratamientos capilares', 'description': 'Tratamientos específicos para el cabello', 'department': departments['Cuidado del Cabello'], 'order_position': 4},
            {'name': 'Styling y fijadores', 'description': 'Productos de styling y fijación', 'department': departments['Cuidado del Cabello'], 'order_position': 5},
            {'name': 'Tintes y coloración', 'description': 'Tintes y productos de coloración', 'department': departments['Cuidado del Cabello'], 'order_position': 6},
            {'name': 'Herramientas de peinado', 'description': 'Planchas, rizadores y secadores', 'department': departments['Cuidado del Cabello'], 'order_position': 7},

            # Departamento 5: FRAGANCIAS (6 categorías)
            {'name': 'Perfumes mujer', 'description': 'Fragancias para mujer', 'department': departments['Fragancias'], 'order_position': 1},
            {'name': 'Perfumes hombre', 'description': 'Fragancias para hombre', 'department': departments['Fragancias'], 'order_position': 2},
            {'name': 'Perfumes unisex', 'description': 'Fragancias unisex', 'department': departments['Fragancias'], 'order_position': 3},
            {'name': 'Aguas de colonia', 'description': 'Aguas de colonia y eau de toilette', 'department': departments['Fragancias'], 'order_position': 4},
            {'name': 'Brumas corporales', 'description': 'Brumas y sprays corporales', 'department': departments['Fragancias'], 'order_position': 5},
            {'name': 'Miniaturas', 'description': 'Miniaturas y sets de fragancias', 'department': departments['Fragancias'], 'order_position': 6},

            # Departamento 6: CUIDADO DE UÑAS (5 categorías)
            {'name': 'Esmaltes de uñas', 'description': 'Esmaltes y lacas de uñas', 'department': departments['Cuidado de Uñas'], 'order_position': 1},
            {'name': 'Tratamientos de uñas', 'description': 'Bases, tops y tratamientos', 'department': departments['Cuidado de Uñas'], 'order_position': 2},
            {'name': 'Quitaesmaltes', 'description': 'Quitaesmaltes y removedores', 'department': departments['Cuidado de Uñas'], 'order_position': 3},
            {'name': 'Herramientas de manicura', 'description': 'Limas, cortaúñas y herramientas', 'department': departments['Cuidado de Uñas'], 'order_position': 4},
            {'name': 'Uñas postizas', 'description': 'Uñas postizas y accesorios', 'department': departments['Cuidado de Uñas'], 'order_position': 5},

            # Departamento 7: ACCESORIOS Y HERRAMIENTAS (6 categorías)
            {'name': 'Brochas de maquillaje', 'description': 'Brochas profesionales de maquillaje', 'department': departments['Accesorios y Herramientas'], 'order_position': 1},
            {'name': 'Esponjas y aplicadores', 'description': 'Esponjas y aplicadores de maquillaje', 'department': departments['Accesorios y Herramientas'], 'order_position': 2},
            {'name': 'Neceseres y organizadores', 'description': 'Neceseres y organizadores de belleza', 'department': departments['Accesorios y Herramientas'], 'order_position': 3},
            {'name': 'Espejos', 'description': 'Espejos de maquillaje y tocador', 'department': departments['Accesorios y Herramientas'], 'order_position': 4},
            {'name': 'Pinzas y tijeras', 'description': 'Pinzas de depilar y tijeras', 'department': departments['Accesorios y Herramientas'], 'order_position': 5},
            {'name': 'Rizadores y planchas', 'description': 'Rizadores, planchas y herramientas térmicas', 'department': departments['Accesorios y Herramientas'], 'order_position': 6},

            # Departamento 8: BEAUTY ACADEMY (4 categorías)
            {'name': 'Consultoría Personalizada', 'description': 'Asesoramiento de belleza one-to-one', 'department': departments['Beauty Academy'], 'order_position': 1},
            {'name': 'Masterclass en Vivo', 'description': 'Clases en directo con expertos', 'department': departments['Beauty Academy'], 'order_position': 2},
            {'name': 'Tutoriales Especializados', 'description': 'Tutoriales avanzados de maquillaje y cuidado', 'department': departments['Beauty Academy'], 'order_position': 3},
            {'name': 'Análisis de Piel y Color', 'description': 'Análisis profesional personalizado', 'department': departments['Beauty Academy'], 'order_position': 4},

            # Departamento 9: PREMIUM SERVICES (4 categorías)
            {'name': 'Gift & Wrapping', 'description': 'Envoltorio de regalo premium', 'department': departments['Premium Services'], 'order_position': 1},
            {'name': 'Envío Express', 'description': 'Envío urgente 24-48h', 'department': departments['Premium Services'], 'order_position': 2},
            {'name': 'Personalización de Productos', 'description': 'Grabado y personalización exclusiva', 'department': departments['Premium Services'], 'order_position': 3},
            {'name': 'Kits y Muestras', 'description': 'Kits personalizados y muestras premium', 'department': departments['Premium Services'], 'order_position': 4},

            # Departamento 10: CLUB EXCLUSIVO (4 categorías)
            {'name': 'Beauty Boxes', 'description': 'Cajas mensuales sorpresa', 'department': departments['Club Exclusivo'], 'order_position': 1},
            {'name': 'Membresías VIP', 'description': 'Acceso VIP y beneficios exclusivos', 'department': departments['Club Exclusivo'], 'order_position': 2},
            {'name': 'Suscripciones Especializadas', 'description': 'Suscripciones temáticas mensuales', 'department': departments['Club Exclusivo'], 'order_position': 3},
            {'name': 'Ediciones Limitadas', 'description': 'Acceso prioritario a lanzamientos', 'department': departments['Club Exclusivo'], 'order_position': 4},
        ]

        categories = {}
        for category_data in categories_data:
            category = Category.objects.create(**category_data)
            categories[category.name] = category
            self.stdout.write(f'Created category: {category.name} (Department: {category.department.name})')

        # Define category-specific images
        category_images = {
            # Maquillaje
            'Bases y correctores': 'https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=800',
            'Polvos': 'https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=800',
            'Coloretes y bronceadores': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800',
            'Iluminadores': 'https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=800',
            'Sombras de ojos': 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800',
            'Delineadores y lápices de ojos': 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800',
            'Máscaras de pestañas': 'https://images.unsplash.com/photo-1631730486572-226d1f595b68?w=800',
            'Labiales': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800',
            'Gloss labial': 'https://images.unsplash.com/photo-1571875257727-256c39da42af?w=800',
            'Brochas y esponjas': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800',

            # Cuidado Facial
            'Limpiadores faciales': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=800',
            'Tónicos': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800',
            'Serums': 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=800',
            'Contornos de ojos': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800',
            'Hidratantes faciales': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800',
            'Mascarillas faciales': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800',
            'Exfoliantes faciales': 'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=800',
            'Protectores solares faciales': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800',

            # Cuidado Corporal
            'Geles y jabones corporales': 'https://images.unsplash.com/photo-1615397349754-cfa2066a298e?w=800',
            'Hidratantes corporales': 'https://images.unsplash.com/photo-1571875257727-256c39da42af?w=800',
            'Exfoliantes corporales': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=800',
            'Aceites corporales': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=800',
            'Protectores solares corporales': 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=800',
            'Desodorantes': 'https://images.unsplash.com/photo-1615397349754-cfa2066a298e?w=800',
            'Cuidado de manos': 'https://images.unsplash.com/photo-1585652757173-57de5e9fab42?w=800',
            'Cuidado de pies': 'https://images.unsplash.com/photo-1571875257727-256c39da42af?w=800',

            # Cuidado del Cabello
            'Champús': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800',
            'Acondicionadores': 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800',
            'Mascarillas capilares': 'https://images.unsplash.com/photo-1619451334792-150fd785ee74?w=800',
            'Tratamientos capilares': 'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800',
            'Styling y fijadores': 'https://images.unsplash.com/photo-1634449571010-02389ed0f9b0?w=800',
            'Tintes y coloración': 'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800',
            'Herramientas de peinado': 'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800',

            # Fragancias
            'Perfumes mujer': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=800',
            'Perfumes hombre': 'https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=800',
            'Perfumes unisex': 'https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=800',
            'Aguas de colonia': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800',
            'Brumas corporales': 'https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800',
            'Miniaturas': 'https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=800',

            # Cuidado de Uñas
            'Esmaltes de uñas': 'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=800',
            'Tratamientos de uñas': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800',
            'Quitaesmaltes': 'https://images.unsplash.com/photo-1607779097040-26e80aa78e66?w=800',
            'Herramientas de manicura': 'https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800',
            'Uñas postizas': 'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=800',

            # Accesorios y Herramientas
            'Brochas de maquillaje': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800',
            'Esponjas y aplicadores': 'https://images.unsplash.com/photo-1598452963314-b09f397a5c48?w=800',
            'Neceseres y organizadores': 'https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800',
            'Espejos': 'https://images.unsplash.com/photo-1618220179428-22790b461013?w=800',
            'Pinzas y tijeras': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800',
            'Rizadores y planchas': 'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800',
        }

        # Create sample products for each category
        self.stdout.write('Creating products...')
        products_created = 0

        for category_name, category in categories.items():
            # Create 2-3 available products per category
            num_products = random.randint(2, 3)
            for i in range(num_products):
                brand = random.choice(list(brands.values()))
                price = round(random.uniform(5.99, 49.99), 2)
                offer_price = round(price * 0.85, 2) if random.random() > 0.7 else None

                product = Product.objects.create(
                    name=f'{category_name} {brand.name} #{i+1}',
                    description=f'Producto de {category_name} de la marca {brand.name}',
                    price=price,
                    offer_price=offer_price,
                    brand=brand,
                    category=category,
                    stock=random.randint(50, 200),
                    is_available=True,
                    is_featured=random.random() > 0.7,
                    gender='Unisex'
                )

                # Add image - use category-specific image
                category_image = category_images.get(category_name, 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800')
                ProductImage.objects.create(
                    product=product,
                    image=category_image,
                    is_main=True,
                    order_position=1
                )

                # Add size
                ProductSize.objects.create(
                    product=product,
                    size='Estándar',
                    stock=product.stock
                )

                products_created += 1

            # Create 5 out-of-stock products per category
            for i in range(5):
                brand = random.choice(list(brands.values()))
                price = round(random.uniform(5.99, 49.99), 2)
                offer_price = round(price * 0.85, 2) if random.random() > 0.5 else None

                product = Product.objects.create(
                    name=f'{category_name} {brand.name} [AGOTADO] #{i+1}',
                    description=f'Producto agotado de {category_name} de la marca {brand.name}',
                    price=price,
                    offer_price=offer_price,
                    brand=brand,
                    category=category,
                    stock=0,
                    is_available=False,
                    is_featured=False,
                    gender='Unisex'
                )

                # Add image - use category-specific image
                category_image = category_images.get(category_name, 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800')
                ProductImage.objects.create(
                    product=product,
                    image=category_image,
                    is_main=True,
                    order_position=1
                )

                # Add size
                ProductSize.objects.create(
                    product=product,
                    size='Estándar',
                    stock=0
                )

                products_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Successfully created {products_created} products!'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(departments)} departments'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(brands)} brands'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories)} categories'))
        self.stdout.write(self.style.SUCCESS('Catalog seeding completed successfully!'))
