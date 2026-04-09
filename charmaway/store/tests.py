import pytest
from django.urls import reverse
from django.test import TestCase
from catalog.models import Product, Department, Category, Brand


# ------------------------------
# FIXTURES
# ------------------------------

@pytest.fixture
def department(db):
    return Department.objects.create(
        name="Maquillaje",
        description="Productos de maquillaje",
        order_position=1
    )


@pytest.fixture
def category(db, department):
    return Category.objects.create(
        name="Labiales",
        description="Labiales de diferentes colores",
        department=department,
        order_position=1
    )


@pytest.fixture
def brand(db):
    return Brand.objects.create(
        name="L'Oréal",
        description="Marca de cosméticos"
    )


@pytest.fixture
def featured_product(db, category, brand):
    return Product.objects.create(
        name="Labial Rojo",
        description="Labial rojo mate",
        price=15.99,
        stock=10,
        is_available=True,
        is_featured=True,
        category=category,
        brand=brand
    )


@pytest.fixture
def regular_product(db, category, brand):
    return Product.objects.create(
        name="Labial Rosa",
        description="Labial rosa brillante",
        price=12.99,
        stock=5,
        is_available=True,
        is_featured=False,
        category=category,
        brand=brand
    )


# ------------------------------
# UNIT TESTS - Models
# ------------------------------

class HomeModelTests(TestCase):
    """Unit tests for models used in home view"""

    def test_product_has_offer_property(self):
        """Test that product.has_offer returns True when offer_price is set"""
        product = Product.objects.create(
            name="Test Product",
            price=20.00,
            offer_price=15.00,
            stock=10
        )
        self.assertTrue(product.has_offer)

    def test_product_no_offer_property(self):
        """Test that product.has_offer returns False when no offer_price"""
        product = Product.objects.create(
            name="Test Product",
            price=20.00,
            stock=10
        )
        self.assertFalse(product.has_offer)

    def test_product_final_price_with_offer(self):
        """Test that final_price returns offer_price when available"""
        product = Product.objects.create(
            name="Test Product",
            price=20.00,
            offer_price=15.00,
            stock=10
        )
        self.assertEqual(product.final_price, 15.00)

    def test_product_final_price_without_offer(self):
        """Test that final_price returns regular price when no offer"""
        product = Product.objects.create(
            name="Test Product",
            price=20.00,
            stock=10
        )
        self.assertEqual(product.final_price, 20.00)

    def test_product_discount_percentage(self):
        """Test discount percentage calculation"""
        product = Product.objects.create(
            name="Test Product",
            price=100.00,
            offer_price=75.00,
            stock=10
        )
        self.assertEqual(product.discount_percentage, 25)

    def test_department_ordering(self):
        """Test that departments are ordered by order_position"""
        dept1 = Department.objects.create(name="Dept A", order_position=2)
        dept2 = Department.objects.create(name="Dept B", order_position=1)

        departments = list(Department.objects.all())
        self.assertEqual(departments[0], dept2)
        self.assertEqual(departments[1], dept1)


# ------------------------------
# INTEGRATION TESTS - Home View
# ------------------------------

@pytest.mark.django_db
def test_home_view_loads(client):
    """Test that home view loads successfully"""
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_view_shows_featured_products(client, featured_product, regular_product):
    """Test that home view displays featured products"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = response.context['featured_products']

    # Featured product should be in the list
    assert featured_product in list(featured_products)
    # Regular product should NOT be in the list (not featured)
    assert regular_product not in list(featured_products)


@pytest.mark.django_db
def test_home_view_excludes_services_department(client, db):
    """Test that home view excludes products from Services departments"""
    # Create Service departments (using the new naming structure)
    beauty_academy = Department.objects.create(name="Beauty Academy", order_position=8)
    beauty_cat = Category.objects.create(
        name="Consultoría Personalizada",
        department=beauty_academy
    )

    premium_services = Department.objects.create(name="Premium Services", order_position=9)
    premium_cat = Category.objects.create(
        name="Gift & Wrapping",
        department=premium_services
    )

    # Create products in Service departments
    service_product1 = Product.objects.create(
        name="Beauty Service Product",
        price=50.00,
        stock=10,
        is_available=True,
        is_featured=True,
        category=beauty_cat
    )

    service_product2 = Product.objects.create(
        name="Premium Service Product",
        price=30.00,
        stock=5,
        is_available=True,
        is_featured=True,
        category=premium_cat
    )

    url = reverse("home")
    response = client.get(url)

    featured_products = list(response.context['featured_products'])
    assert service_product1 not in featured_products
    assert service_product2 not in featured_products


@pytest.mark.django_db
def test_home_view_shows_departments(client, department):
    """Test that home view displays departments"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    departments = response.context['departments']

    assert department in list(departments)


@pytest.mark.django_db
def test_home_view_limits_featured_products(client, category, brand):
    """Test that home view limits featured products to 8"""
    # Create 10 featured products
    for i in range(10):
        Product.objects.create(
            name=f"Featured Product {i}",
            price=10.00,
            stock=10,
            is_available=True,
            is_featured=True,
            category=category,
            brand=brand
        )

    url = reverse("home")
    response = client.get(url)

    featured_products = response.context['featured_products']
    assert len(featured_products) <= 8


# ------------------------------
# INTERFACE TESTS - Home View
# ------------------------------

@pytest.mark.django_db
def test_home_template_rendering(client, featured_product, department):
    """Test that home template renders correctly with content"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert b"Labial Rojo" in response.content
    assert b"Maquillaje" in response.content


@pytest.mark.django_db
def test_home_context_has_required_data(client, department):
    """Test that home view context contains required data"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert 'featured_products' in response.context
    assert 'departments' in response.context


# ------------------------------
# INTEGRATION TESTS - About View
# ------------------------------

@pytest.mark.django_db
def test_about_view_loads(client):
    """Test that about view loads successfully"""
    url = reverse("about")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_template_used(client):
    """Test that about view uses correct template"""
    url = reverse("about")
    response = client.get(url)
    assert response.status_code == 200
    assert 'store/about.html' in [t.name for t in response.templates]


# ------------------------------
# EDGE CASE TESTS - Home View
# ------------------------------

@pytest.mark.django_db
def test_home_view_no_featured_products(client, department):
    """Test home view when there are no featured products"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = response.context['featured_products']
    assert len(featured_products) == 0


@pytest.mark.django_db
def test_home_view_no_departments(client):
    """Test home view when there are no departments"""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    departments = response.context['departments']
    assert len(departments) == 0


@pytest.mark.django_db
def test_home_view_products_not_available(client, category, brand):
    """Test that home view excludes products with is_available=False"""
    # Create unavailable featured product
    unavailable_product = Product.objects.create(
        name="Unavailable Product",
        price=15.99,
        stock=10,
        is_available=False,  # Not available
        is_featured=True,
        category=category,
        brand=brand
    )

    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = list(response.context['featured_products'])
    assert unavailable_product not in featured_products


@pytest.mark.django_db
def test_home_view_product_without_brand(client, category):
    """Test home view with featured product without brand"""
    product = Product.objects.create(
        name="Product No Brand",
        price=15.99,
        stock=10,
        is_available=True,
        is_featured=True,
        category=category,
        brand=None
    )

    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = list(response.context['featured_products'])
    assert product in featured_products


@pytest.mark.django_db
def test_home_view_product_without_category(client, brand):
    """Test home view with featured product without category"""
    product = Product.objects.create(
        name="Product No Category",
        price=15.99,
        stock=10,
        is_available=True,
        is_featured=True,
        category=None,
        brand=brand
    )

    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = list(response.context['featured_products'])
    assert product in featured_products


@pytest.mark.django_db
def test_home_view_multiple_departments(client, category, brand):
    """Test home view with products from multiple departments"""
    # Create second department
    dept2 = Department.objects.create(
        name="Fragancias",
        description="Perfumes y fragancias",
        order_position=2
    )
    cat2 = Category.objects.create(
        name="Perfumes",
        description="Perfumes de diferentes aromas",
        department=dept2,
        order_position=1
    )

    # Create featured products from different departments
    product1 = Product.objects.create(
        name="Product Dept 1",
        price=15.99,
        stock=10,
        is_available=True,
        is_featured=True,
        category=category,
        brand=brand
    )
    product2 = Product.objects.create(
        name="Product Dept 2",
        price=25.99,
        stock=10,
        is_available=True,
        is_featured=True,
        category=cat2,
        brand=brand
    )

    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    featured_products = list(response.context['featured_products'])
    # Both products should appear
    assert product1 in featured_products
    assert product2 in featured_products
    # Both departments should appear
    departments = list(response.context['departments'])
    assert len(departments) == 2
