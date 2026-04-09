import pytest
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from catalog.models import Product, Department, Category, Brand, ProductImage, ProductSize


# ------------------------------
# FIXTURES
# ------------------------------

@pytest.fixture
def department(db):
    return Department.objects.create(
        name="Cuidado de la Piel",
        description="Productos para el cuidado facial",
        order_position=1
    )


@pytest.fixture
def category(db, department):
    return Category.objects.create(
        name="Cremas",
        description="Cremas faciales",
        department=department,
        order_position=1
    )


@pytest.fixture
def brand(db):
    return Brand.objects.create(
        name="Nivea",
        description="Marca de cosméticos"
    )


@pytest.fixture
def product(db, category, brand):
    return Product.objects.create(
        name="Crema Hidratante",
        description="Crema hidratante para piel seca",
        price=Decimal("25.99"),
        stock=15,
        is_available=True,
        category=category,
        brand=brand
    )


@pytest.fixture
def product_with_offer(db, category, brand):
    return Product.objects.create(
        name="Crema Antiedad",
        description="Crema antiedad con retinol",
        price=Decimal("50.00"),
        offer_price=Decimal("35.00"),
        stock=10,
        is_available=True,
        category=category,
        brand=brand
    )


@pytest.fixture
def product_with_images(db, product):
    ProductImage.objects.create(
        product=product,
        image="https://example.com/main.jpg",
        is_main=True,
        order_position=1
    )
    ProductImage.objects.create(
        product=product,
        image="https://example.com/secondary.jpg",
        is_main=False,
        order_position=2
    )
    return product


@pytest.fixture
def product_with_sizes(db, product):
    ProductSize.objects.create(product=product, size="50ml", stock=5)
    ProductSize.objects.create(product=product, size="100ml", stock=10)
    return product


# ------------------------------
# UNIT TESTS - Models
# ------------------------------

class CatalogModelTests(TestCase):
    """Unit tests for catalog models"""

    def test_product_str_representation(self):
        """Test product string representation"""
        product = Product.objects.create(
            name="Test Product",
            price=Decimal("10.00"),
            stock=5
        )
        self.assertEqual(str(product), "Test Product")

    def test_category_str_representation(self):
        """Test category string representation"""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")

    def test_brand_str_representation(self):
        """Test brand string representation"""
        brand = Brand.objects.create(name="Test Brand")
        self.assertEqual(str(brand), "Test Brand")

    def test_product_has_offer_true(self):
        """Test has_offer property returns True when offer exists"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("100.00"),
            offer_price=Decimal("80.00"),
            stock=5
        )
        self.assertTrue(product.has_offer)

    def test_product_has_offer_false(self):
        """Test has_offer property returns False when no offer"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("100.00"),
            stock=5
        )
        self.assertFalse(product.has_offer)

    def test_product_final_price_with_offer(self):
        """Test final_price returns offer_price when available"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("100.00"),
            offer_price=Decimal("80.00"),
            stock=5
        )
        self.assertEqual(product.final_price, Decimal("80.00"))

    def test_product_final_price_without_offer(self):
        """Test final_price returns regular price when no offer"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("100.00"),
            stock=5
        )
        self.assertEqual(product.final_price, Decimal("100.00"))

    def test_product_discount_percentage(self):
        """Test discount percentage calculation"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("100.00"),
            offer_price=Decimal("75.00"),
            stock=5
        )
        self.assertEqual(product.discount_percentage, 25)

    def test_product_size_unique_together(self):
        """Test that product and size combination is unique"""
        product = Product.objects.create(
            name="Product",
            price=Decimal("10.00"),
            stock=5
        )
        ProductSize.objects.create(product=product, size="M", stock=10)

        # This should raise an error due to unique_together constraint
        with self.assertRaises(Exception):
            ProductSize.objects.create(product=product, size="M", stock=5)


# ------------------------------
# INTEGRATION TESTS - Catalog View
# ------------------------------

@pytest.mark.django_db
def test_catalog_view_loads(client):
    """Test that catalog view loads successfully"""
    url = reverse("catalog:catalog")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_catalog_view_shows_products(client, product):
    """Test that catalog view displays products"""
    url = reverse("catalog:catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_excludes_services_department(client, db):
    """Test that catalog excludes products from Services department"""
    services_dept = Department.objects.create(name="Servicios", order_position=8)
    services_cat = Category.objects.create(
        name="Asesoramiento",
        department=services_dept
    )
    service_product = Product.objects.create(
        name="Service Product",
        price=Decimal("50.00"),
        stock=10,
        category=services_cat
    )

    url = reverse("catalog:catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert service_product.name.encode() not in response.content


@pytest.mark.django_db
def test_catalog_filter_by_department(client, product, department):
    """Test filtering products by department"""
    url = reverse("catalog:catalog") + f"?department={department.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_filter_by_category(client, product, category):
    """Test filtering products by category"""
    url = reverse("catalog:catalog") + f"?category={category.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_filter_by_brand(client, product, brand):
    """Test filtering products by brand"""
    url = reverse("catalog:catalog") + f"?brand={brand.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_search_by_name(client, product):
    """Test searching products by name"""
    url = reverse("catalog:catalog") + f"?q={product.name}"
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_search_by_description(client, product):
    """Test searching products by description"""
    url = reverse("catalog:catalog") + "?q=hidratante"
    response = client.get(url)

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_sort_by_name(client, category, brand):
    """Test sorting products by name"""
    Product.objects.create(name="Zebra Product", price=Decimal("10.00"), stock=5, category=category, brand=brand)
    Product.objects.create(name="Alpha Product", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?sort=name"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert products[0].name == "Alpha Product"


@pytest.mark.django_db
def test_catalog_sort_by_price_asc(client, category, brand):
    """Test sorting products by price ascending"""
    Product.objects.create(name="Expensive", price=Decimal("100.00"), stock=5, category=category, brand=brand)
    Product.objects.create(name="Cheap", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?sort=price_asc"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert products[0].name == "Cheap"


@pytest.mark.django_db
def test_catalog_sort_by_price_desc(client, category, brand):
    """Test sorting products by price descending"""
    Product.objects.create(name="Expensive", price=Decimal("100.00"), stock=5, category=category, brand=brand)
    Product.objects.create(name="Cheap", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?sort=price_desc"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert products[0].name == "Expensive"


@pytest.mark.django_db
def test_catalog_pagination(client, category, brand):
    """Test pagination in catalog"""
    # Create 30 products
    for i in range(30):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=24"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_catalog_pagination_page_2(client, category, brand):
    """Test accessing second page of catalog"""
    # Create 30 products
    for i in range(30):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=24&page=2"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['page_obj'].number == 2


# ------------------------------
# INTEGRATION TESTS - Product Detail View
# ------------------------------

@pytest.mark.django_db
def test_product_detail_view_loads(client, product):
    """Test that product detail view loads successfully"""
    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_detail_shows_correct_product(client, product):
    """Test that product detail shows correct product information"""
    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['product'] == product
    assert product.name.encode() in response.content
    assert product.description.encode() in response.content


@pytest.mark.django_db
def test_product_detail_nonexistent_returns_404(client):
    """Test that accessing nonexistent product returns 404"""
    url = reverse("catalog:product_detail", args=[99999])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_product_detail_shows_images(client, product_with_images):
    """Test that product detail shows product images"""
    url = reverse("catalog:product_detail", args=[product_with_images.id])
    response = client.get(url)

    assert response.status_code == 200
    images = response.context['images']
    assert len(images) == 2


@pytest.mark.django_db
def test_product_detail_shows_main_image(client, product_with_images):
    """Test that product detail identifies main image"""
    url = reverse("catalog:product_detail", args=[product_with_images.id])
    response = client.get(url)

    assert response.status_code == 200
    main_image = response.context['main_image']
    assert main_image is not None
    assert main_image.is_main is True


@pytest.mark.django_db
def test_product_detail_shows_sizes(client, product_with_sizes):
    """Test that product detail shows available sizes"""
    url = reverse("catalog:product_detail", args=[product_with_sizes.id])
    response = client.get(url)

    assert response.status_code == 200
    sizes = response.context['sizes']
    assert len(sizes) == 2
    assert any(s.size == "50ml" for s in sizes)
    assert any(s.size == "100ml" for s in sizes)


# ------------------------------
# INTERFACE TESTS - Catalog
# ------------------------------

@pytest.mark.django_db
def test_catalog_context_has_required_data(client, category, brand):
    """Test that catalog view context contains required data"""
    url = reverse("catalog:catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert 'products' in response.context
    assert 'page_obj' in response.context
    assert 'categories' in response.context
    assert 'brands' in response.context


@pytest.mark.django_db
def test_catalog_template_rendering(client, product):
    """Test that catalog template renders correctly"""
    url = reverse("catalog:catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert 'catalog/catalog.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_product_detail_context_has_required_data(client, product):
    """Test that product detail context contains required data"""
    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'product' in response.context
    assert 'images' in response.context
    assert 'sizes' in response.context


@pytest.mark.django_db
def test_product_detail_template_rendering(client, product):
    """Test that product detail template renders correctly"""
    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'catalog/product_detail.html' in [t.name for t in response.templates]


# ------------------------------
# EDGE CASE TESTS - Catalog Filters
# ------------------------------

@pytest.mark.django_db
def test_catalog_filter_by_invalid_department(client):
    """Test filtering by non-existent department ID"""
    url = reverse("catalog:catalog") + "?department=99999"
    response = client.get(url)

    assert response.status_code == 200
    # Should return empty results or all products
    assert 'products' in response.context


@pytest.mark.django_db
def test_catalog_filter_by_empty_department(client, product):
    """Test filtering with empty department parameter"""
    url = reverse("catalog:catalog") + "?department="
    response = client.get(url)

    assert response.status_code == 200
    # Should show all products when parameter is empty
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_filter_by_invalid_category(client):
    """Test filtering by non-existent category ID"""
    url = reverse("catalog:catalog") + "?category=99999"
    response = client.get(url)

    assert response.status_code == 200
    assert 'products' in response.context


@pytest.mark.django_db
def test_catalog_filter_by_empty_category(client, product):
    """Test filtering with empty category parameter"""
    url = reverse("catalog:catalog") + "?category="
    response = client.get(url)

    assert response.status_code == 200
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_filter_by_multiple_brands(client, category):
    """Test filtering by multiple brands using getlist"""
    brand1 = Brand.objects.create(name="Brand A")
    brand2 = Brand.objects.create(name="Brand B")
    brand3 = Brand.objects.create(name="Brand C")

    product1 = Product.objects.create(name="Product A", price=Decimal("10.00"), stock=5, category=category, brand=brand1)
    product2 = Product.objects.create(name="Product B", price=Decimal("10.00"), stock=5, category=category, brand=brand2)
    product3 = Product.objects.create(name="Product C", price=Decimal("10.00"), stock=5, category=category, brand=brand3)

    # Filter by brand1 and brand2
    url = reverse("catalog:catalog") + f"?brand={brand1.id}&brand={brand2.id}"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert product1 in products
    assert product2 in products
    assert product3 not in products


@pytest.mark.django_db
def test_catalog_combined_filters(client, department, category, brand):
    """Test combining department, category, and brand filters"""
    product = Product.objects.create(
        name="Filtered Product",
        price=Decimal("20.00"),
        stock=5,
        category=category,
        brand=brand
    )

    # Create product in different department
    other_dept = Department.objects.create(name="Other Dept", order_position=2)
    other_cat = Category.objects.create(name="Other Cat", department=other_dept)
    other_product = Product.objects.create(
        name="Other Product",
        price=Decimal("15.00"),
        stock=5,
        category=other_cat,
        brand=brand
    )

    url = reverse("catalog:catalog") + f"?department={department.id}&category={category.id}&brand={brand.id}"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert product in products
    assert other_product not in products


# ------------------------------
# EDGE CASE TESTS - Search
# ------------------------------

@pytest.mark.django_db
def test_catalog_search_empty_query(client, product):
    """Test searching with empty query parameter"""
    url = reverse("catalog:catalog") + "?q="
    response = client.get(url)

    assert response.status_code == 200
    # Empty search should show all products
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_search_whitespace_only(client, product):
    """Test searching with only whitespace"""
    url = reverse("catalog:catalog") + "?q=   "
    response = client.get(url)

    assert response.status_code == 200
    # Whitespace-only search should show all products
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_search_no_results(client, category, brand):
    """Test searching with query that returns no results"""
    Product.objects.create(name="Product A", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?q=nonexistentproduct12345"
    response = client.get(url)

    assert response.status_code == 200
    products = list(response.context['products'])
    assert len(products) == 0


@pytest.mark.django_db
def test_catalog_search_by_brand_name(client, category):
    """Test searching by brand name"""
    brand = Brand.objects.create(name="UniqueSpecialBrand")
    product = Product.objects.create(
        name="Some Product",
        price=Decimal("10.00"),
        stock=5,
        category=category,
        brand=brand
    )

    url = reverse("catalog:catalog") + "?q=UniqueSpecialBrand"
    response = client.get(url)

    assert response.status_code == 200
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_search_combined_with_filters(client, department, category, brand):
    """Test combining search with filters"""
    product = Product.objects.create(
        name="Special Product",
        description="This is special",
        price=Decimal("10.00"),
        stock=5,
        category=category,
        brand=brand
    )

    url = reverse("catalog:catalog") + f"?q=special&department={department.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert product in list(response.context['products'])


# ------------------------------
# EDGE CASE TESTS - Sorting
# ------------------------------

@pytest.mark.django_db
def test_catalog_sort_invalid_option(client, category, brand):
    """Test sorting with invalid sort option"""
    product = Product.objects.create(name="Product", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?sort=invalid_option"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 'name' sorting
    assert product in list(response.context['products'])


@pytest.mark.django_db
def test_catalog_sort_empty_parameter(client, category, brand):
    """Test sorting with empty sort parameter"""
    product = Product.objects.create(name="Product", price=Decimal("10.00"), stock=5, category=category, brand=brand)

    url = reverse("catalog:catalog") + "?sort="
    response = client.get(url)

    assert response.status_code == 200
    assert product in list(response.context['products'])


# ------------------------------
# EDGE CASE TESTS - Pagination
# ------------------------------

@pytest.mark.django_db
def test_catalog_pagination_per_page_36(client, category, brand):
    """Test pagination with 36 items per page"""
    # Create 40 products
    for i in range(40):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=36"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['products']) == 36
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_catalog_pagination_per_page_48(client, category, brand):
    """Test pagination with 48 items per page"""
    # Create 50 products
    for i in range(50):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=48"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['products']) == 48
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_catalog_pagination_invalid_per_page(client, category, brand):
    """Test pagination with invalid per_page value"""
    for i in range(30):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=999"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 24
    assert len(response.context['products']) == 24


@pytest.mark.django_db
def test_catalog_pagination_per_page_string(client, category, brand):
    """Test pagination with string per_page value"""
    for i in range(30):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=abc"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 24
    assert len(response.context['products']) == 24


@pytest.mark.django_db
def test_catalog_pagination_invalid_page_number(client, category, brand):
    """Test pagination with invalid page number"""
    for i in range(30):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=24&page=abc"
    response = client.get(url)

    assert response.status_code == 200
    # Django's get_page handles this gracefully


@pytest.mark.django_db
def test_catalog_pagination_page_out_of_range(client, category, brand):
    """Test pagination with page number beyond available pages"""
    for i in range(10):
        Product.objects.create(
            name=f"Product {i}",
            price=Decimal("10.00"),
            stock=5,
            category=category,
            brand=brand
        )

    url = reverse("catalog:catalog") + "?per_page=24&page=99999"
    response = client.get(url)

    assert response.status_code == 200
    # get_page returns last page when out of range
    page_obj = response.context['page_obj']
    assert page_obj.number == page_obj.paginator.num_pages


# ------------------------------
# EDGE CASE TESTS - Product Detail
# ------------------------------

@pytest.mark.django_db
def test_product_detail_without_images(client, category, brand):
    """Test product detail for product without images"""
    product = Product.objects.create(
        name="Product No Images",
        price=Decimal("10.00"),
        stock=5,
        category=category,
        brand=brand
    )

    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['main_image'] is None
    assert len(response.context['images']) == 0


@pytest.mark.django_db
def test_product_detail_without_sizes(client, category, brand):
    """Test product detail for product without sizes"""
    product = Product.objects.create(
        name="Product No Sizes",
        price=Decimal("10.00"),
        stock=5,
        category=category,
        brand=brand
    )

    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['sizes']) == 0


@pytest.mark.django_db
def test_product_detail_without_brand(client, category):
    """Test product detail for product without brand"""
    product = Product.objects.create(
        name="Product No Brand",
        price=Decimal("10.00"),
        stock=5,
        category=category,
        brand=None
    )

    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['product'].brand is None


@pytest.mark.django_db
def test_product_detail_without_category(client, brand):
    """Test product detail for product without category"""
    product = Product.objects.create(
        name="Product No Category",
        price=Decimal("10.00"),
        stock=5,
        category=None,
        brand=brand
    )

    url = reverse("catalog:product_detail", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['product'].category is None
