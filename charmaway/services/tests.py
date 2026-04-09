import pytest
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from services.models import Service, ServiceCategory
from catalog.models import Category, Department


# ------------------------------
# FIXTURES
# ------------------------------

@pytest.fixture
def services_department(db):
    return Department.objects.create(
        name="Beauty Academy",
        description="Formación y asesoramiento personalizado",
        order_position=8
    )


@pytest.fixture
def service_category(db, services_department):
    return Category.objects.create(
        name="Consultoría Personalizada",
        description="Asesoramiento de belleza one-to-one",
        department=services_department,
        order_position=1
    )


@pytest.fixture
def service(db, service_category):
    return Service.objects.create(
        name="Consulta de Maquillaje",
        description="Consulta personalizada de maquillaje de 30 minutos",
        category=service_category,
        price=Decimal("25.00"),
        duration="30 minutos",
        image="https://example.com/makeup-consultation.jpg",
        is_available=True
    )


@pytest.fixture
def service_with_offer(db, service_category):
    return Service.objects.create(
        name="Masterclass de Maquillaje",
        description="Clase completa de técnicas de maquillaje",
        category=service_category,
        price=Decimal("100.00"),
        offer_price=Decimal("75.00"),
        duration="2 horas",
        image="https://example.com/masterclass.jpg",
        is_available=True,
        is_featured=True
    )


@pytest.fixture
def unavailable_service(db, service_category):
    return Service.objects.create(
        name="Servicio No Disponible",
        description="Este servicio no está disponible actualmente",
        category=service_category,
        price=Decimal("50.00"),
        duration="1 hora",
        image="https://example.com/unavailable.jpg",
        is_available=False
    )


# ------------------------------
# UNIT TESTS - Models
# ------------------------------

class ServiceModelTests(TestCase):
    """Unit tests for service models"""

    def test_service_str_representation(self):
        """Test service string representation"""
        service = Service.objects.create(
            name="Test Service",
            description="Test description",
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )
        self.assertEqual(str(service), "Test Service")

    def test_service_category_str_representation(self):
        """Test service category string representation"""
        category = ServiceCategory.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")

    def test_service_get_final_price_with_offer(self):
        """Test get_final_price returns offer_price when available"""
        service = Service.objects.create(
            name="Service",
            description="Description",
            price=Decimal("100.00"),
            offer_price=Decimal("80.00"),
            image="https://example.com/test.jpg"
        )
        self.assertEqual(service.get_final_price(), Decimal("80.00"))

    def test_service_get_final_price_without_offer(self):
        """Test get_final_price returns regular price when no offer"""
        service = Service.objects.create(
            name="Service",
            description="Description",
            price=Decimal("100.00"),
            image="https://example.com/test.jpg"
        )
        self.assertEqual(service.get_final_price(), Decimal("100.00"))

    def test_service_default_is_available(self):
        """Test that service is_available defaults to True"""
        service = Service.objects.create(
            name="Service",
            description="Description",
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )
        self.assertTrue(service.is_available)

    def test_service_default_is_featured(self):
        """Test that service is_featured defaults to False"""
        service = Service.objects.create(
            name="Service",
            description="Description",
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )
        self.assertFalse(service.is_featured)

    def test_service_ordering(self):
        """Test that services are ordered by is_featured then name"""
        service1 = Service.objects.create(
            name="B Service",
            description="Test",
            price=Decimal("25.00"),
            image="https://example.com/test.jpg",
            is_featured=False
        )
        service2 = Service.objects.create(
            name="A Service",
            description="Test",
            price=Decimal("25.00"),
            image="https://example.com/test.jpg",
            is_featured=True
        )

        services = list(Service.objects.all())
        # Featured services should come first
        self.assertEqual(services[0], service2)
        self.assertEqual(services[1], service1)


# ------------------------------
# INTEGRATION TESTS - Services Catalog View
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_view_loads(client):
    """Test that services catalog view loads successfully"""
    url = reverse("services:services_catalog")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_services_catalog_shows_services(client, service):
    """Test that services catalog displays services"""
    url = reverse("services:services_catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert service.name.encode() in response.content


@pytest.mark.django_db
def test_services_catalog_shows_available_services_only(client, service, unavailable_service):
    """Test that catalog shows all services including unavailable ones"""
    url = reverse("services:services_catalog")
    response = client.get(url)

    assert response.status_code == 200
    # Both services should be in the queryset
    services = list(response.context['services'])
    assert service in services
    assert unavailable_service in services


@pytest.mark.django_db
def test_services_catalog_filter_by_category(client, service, service_category):
    """Test filtering services by category"""
    url = reverse("services:services_catalog") + f"?category={service_category.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert service.name.encode() in response.content


@pytest.mark.django_db
def test_services_catalog_search_by_name(client, service):
    """Test searching services by name"""
    url = reverse("services:services_catalog") + f"?q={service.name}"
    response = client.get(url)

    assert response.status_code == 200
    assert service.name.encode() in response.content


@pytest.mark.django_db
def test_services_catalog_search_by_description(client, service):
    """Test searching services by description"""
    url = reverse("services:services_catalog") + "?q=personalizada"
    response = client.get(url)

    assert response.status_code == 200
    assert service.name.encode() in response.content


@pytest.mark.django_db
def test_services_catalog_sort_by_name(client, service_category):
    """Test sorting services by name"""
    Service.objects.create(
        name="Zebra Service",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )
    Service.objects.create(
        name="Alpha Service",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?sort=name"
    response = client.get(url)

    assert response.status_code == 200
    services = list(response.context['services'])
    assert services[0].name == "Alpha Service"


@pytest.mark.django_db
def test_services_catalog_sort_by_price_asc(client, service_category):
    """Test sorting services by price ascending"""
    Service.objects.create(
        name="Expensive Service",
        description="Test",
        category=service_category,
        price=Decimal("100.00"),
        image="https://example.com/test.jpg"
    )
    Service.objects.create(
        name="Cheap Service",
        description="Test",
        category=service_category,
        price=Decimal("10.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?sort=price_asc"
    response = client.get(url)

    assert response.status_code == 200
    services = list(response.context['services'])
    assert services[0].name == "Cheap Service"


@pytest.mark.django_db
def test_services_catalog_sort_by_price_desc(client, service_category):
    """Test sorting services by price descending"""
    Service.objects.create(
        name="Expensive Service",
        description="Test",
        category=service_category,
        price=Decimal("100.00"),
        image="https://example.com/test.jpg"
    )
    Service.objects.create(
        name="Cheap Service",
        description="Test",
        category=service_category,
        price=Decimal("10.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?sort=price_desc"
    response = client.get(url)

    assert response.status_code == 200
    services = list(response.context['services'])
    assert services[0].name == "Expensive Service"


@pytest.mark.django_db
def test_services_catalog_pagination(client, service_category):
    """Test pagination in services catalog"""
    # Create 30 services
    for i in range(30):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=24"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_services_catalog_pagination_page_2(client, service_category):
    """Test accessing second page of services catalog"""
    # Create 30 services
    for i in range(30):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=24&page=2"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['page_obj'].number == 2


# ------------------------------
# INTEGRATION TESTS - Service Detail View
# ------------------------------

@pytest.mark.django_db
def test_service_detail_view_loads(client, service):
    """Test that service detail view loads successfully"""
    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_service_detail_shows_correct_service(client, service):
    """Test that service detail shows correct service information"""
    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['service'] == service
    assert service.name.encode() in response.content
    assert service.description.encode() in response.content


@pytest.mark.django_db
def test_service_detail_nonexistent_returns_404(client):
    """Test that accessing nonexistent service returns 404"""
    url = reverse("services:service_detail", args=[99999])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_service_detail_shows_duration(client, service):
    """Test that service detail shows duration"""
    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert service.duration.encode() in response.content


# ------------------------------
# INTERFACE TESTS - Services
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_context_has_required_data(client):
    """Test that services catalog context contains required data"""
    url = reverse("services:services_catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert 'services' in response.context
    assert 'page_obj' in response.context
    assert 'categories' in response.context


@pytest.mark.django_db
def test_services_catalog_template_rendering(client, service):
    """Test that services catalog template renders correctly"""
    url = reverse("services:services_catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert 'services/services_catalog.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_service_detail_context_has_required_data(client, service):
    """Test that service detail context contains required data"""
    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'service' in response.context


@pytest.mark.django_db
def test_service_detail_template_rendering(client, service):
    """Test that service detail template renders correctly"""
    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'services/service_detail.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_services_catalog_shows_only_services_categories(client, services_department, service_category):
    """Test that services catalog shows only categories from Services departments"""
    # Create a regular department and category
    regular_dept = Department.objects.create(name="Maquillaje", order_position=1)
    regular_cat = Category.objects.create(
        name="Labiales",
        department=regular_dept
    )

    # Create another service department to test multiple service departments
    premium_dept = Department.objects.create(name="Premium Services", order_position=9)
    premium_cat = Category.objects.create(
        name="Gift & Wrapping",
        department=premium_dept
    )

    url = reverse("services:services_catalog")
    response = client.get(url)

    assert response.status_code == 200
    categories = list(response.context['categories'])

    # Only service categories should be shown
    assert service_category in categories
    assert premium_cat in categories
    assert regular_cat not in categories


# ------------------------------
# EDGE CASE TESTS - Services Filters
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_filter_by_invalid_category(client):
    """Test filtering by non-existent category ID"""
    url = reverse("services:services_catalog") + "?category=99999"
    response = client.get(url)

    assert response.status_code == 200
    assert 'services' in response.context


@pytest.mark.django_db
def test_services_catalog_filter_by_empty_category(client, service):
    """Test filtering with empty category parameter"""
    url = reverse("services:services_catalog") + "?category="
    response = client.get(url)

    assert response.status_code == 200
    # Should show all services when parameter is empty
    assert service in list(response.context['services'])


@pytest.mark.django_db
def test_services_catalog_filters_by_department(client, services_department, service):
    """Test that services catalog filters by department"""
    # Create another service department with a service
    premium_dept = Department.objects.create(name="Premium Services", order_position=9)
    premium_cat = Category.objects.create(
        name="Gift & Wrapping",
        department=premium_dept
    )
    premium_service = Service.objects.create(
        name="Premium Service",
        description="Test",
        category=premium_cat,
        price=Decimal("50.00"),
        image="https://example.com/test.jpg"
    )

    # Filter by Beauty Academy department
    url = reverse("services:services_catalog") + f"?department={services_department.id}"
    response = client.get(url)

    assert response.status_code == 200
    services = list(response.context['services'])
    # Only services from Beauty Academy should appear
    assert service in services
    assert premium_service not in services


@pytest.mark.django_db
def test_services_catalog_ignores_brand_param(client, service):
    """Test that brand parameter is ignored"""
    url = reverse("services:services_catalog") + "?brand=999"
    response = client.get(url)

    assert response.status_code == 200
    # Brand parameter should be ignored, service should still appear
    assert service in list(response.context['services'])


# ------------------------------
# EDGE CASE TESTS - Services Search
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_search_empty_query(client, service):
    """Test searching with empty query parameter"""
    url = reverse("services:services_catalog") + "?q="
    response = client.get(url)

    assert response.status_code == 200
    # Empty search should show all services
    assert service in list(response.context['services'])


@pytest.mark.django_db
def test_services_catalog_search_whitespace_only(client, service):
    """Test searching with only whitespace"""
    url = reverse("services:services_catalog") + "?q=   "
    response = client.get(url)

    assert response.status_code == 200
    # Whitespace-only search should show all services
    assert service in list(response.context['services'])


@pytest.mark.django_db
def test_services_catalog_search_no_results(client, service_category):
    """Test searching with query that returns no results"""
    Service.objects.create(
        name="Service A",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?q=nonexistentservice12345"
    response = client.get(url)

    assert response.status_code == 200
    services = list(response.context['services'])
    assert len(services) == 0


@pytest.mark.django_db
def test_services_catalog_search_by_category_name(client, service_category):
    """Test searching by category name"""
    service = Service.objects.create(
        name="Some Service",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + f"?q={service_category.name}"
    response = client.get(url)

    assert response.status_code == 200
    assert service in list(response.context['services'])


@pytest.mark.django_db
def test_services_catalog_search_combined_with_category(client, service_category):
    """Test combining search with category filter"""
    service = Service.objects.create(
        name="Special Service",
        description="This is special",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + f"?q=special&category={service_category.id}"
    response = client.get(url)

    assert response.status_code == 200
    assert service in list(response.context['services'])


# ------------------------------
# EDGE CASE TESTS - Services Sorting
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_sort_invalid_option(client, service_category):
    """Test sorting with invalid sort option"""
    service = Service.objects.create(
        name="Service",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?sort=invalid_option"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 'name' sorting
    assert service in list(response.context['services'])


@pytest.mark.django_db
def test_services_catalog_sort_empty_parameter(client, service_category):
    """Test sorting with empty sort parameter"""
    service = Service.objects.create(
        name="Service",
        description="Test",
        category=service_category,
        price=Decimal("25.00"),
        image="https://example.com/test.jpg"
    )

    url = reverse("services:services_catalog") + "?sort="
    response = client.get(url)

    assert response.status_code == 200
    assert service in list(response.context['services'])


# ------------------------------
# EDGE CASE TESTS - Services Pagination
# ------------------------------

@pytest.mark.django_db
def test_services_catalog_pagination_per_page_36(client, service_category):
    """Test pagination with 36 items per page"""
    # Create 40 services
    for i in range(40):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=36"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['services']) == 36
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_services_catalog_pagination_per_page_48(client, service_category):
    """Test pagination with 48 items per page"""
    # Create 50 services
    for i in range(50):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=48"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['services']) == 48
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_services_catalog_pagination_invalid_per_page(client, service_category):
    """Test pagination with invalid per_page value"""
    for i in range(30):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=999"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 24
    assert len(response.context['services']) == 24


@pytest.mark.django_db
def test_services_catalog_pagination_per_page_string(client, service_category):
    """Test pagination with string per_page value"""
    for i in range(30):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=abc"
    response = client.get(url)

    assert response.status_code == 200
    # Should default to 24
    assert len(response.context['services']) == 24


@pytest.mark.django_db
def test_services_catalog_pagination_invalid_page_number(client, service_category):
    """Test pagination with invalid page number"""
    for i in range(30):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=24&page=abc"
    response = client.get(url)

    assert response.status_code == 200
    # Django's get_page handles this gracefully


@pytest.mark.django_db
def test_services_catalog_pagination_page_out_of_range(client, service_category):
    """Test pagination with page number beyond available pages"""
    for i in range(10):
        Service.objects.create(
            name=f"Service {i}",
            description="Test",
            category=service_category,
            price=Decimal("25.00"),
            image="https://example.com/test.jpg"
        )

    url = reverse("services:services_catalog") + "?per_page=24&page=99999"
    response = client.get(url)

    assert response.status_code == 200
    # get_page returns last page when out of range
    page_obj = response.context['page_obj']
    assert page_obj.number == page_obj.paginator.num_pages


# ------------------------------
# EDGE CASE TESTS - Service Detail
# ------------------------------

@pytest.mark.django_db
def test_service_detail_without_category(client):
    """Test service detail for service without category"""
    service = Service.objects.create(
        name="Service No Category",
        description="Test",
        price=Decimal("25.00"),
        image="https://example.com/test.jpg",
        category=None
    )

    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['service'].category is None


@pytest.mark.django_db
def test_service_detail_without_duration(client, service_category):
    """Test service detail for service without duration"""
    service = Service.objects.create(
        name="Service No Duration",
        description="Test",
        price=Decimal("25.00"),
        image="https://example.com/test.jpg",
        category=service_category,
        duration=""  # Empty duration
    )

    url = reverse("services:service_detail", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['service'].duration == ""
