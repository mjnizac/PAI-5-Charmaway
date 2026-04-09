import pytest
from decimal import Decimal
from django.urls import reverse
from order.models import Order, Cart
from catalog.models import Product
from services.models import Service
from customer.models import Customer

# ------------------------------
# FIXTURES
# ------------------------------

@pytest.fixture
def customer(db):
    return Customer.objects.create_user(
        email="cliente@example.com",
        password="password1234",
        name="Juan",
        surnames="Pérez Gómez",
        phone="+34123456789",
        address="Calle Falsa 123",
        city="Madrid",
        zip_code="28001"
    )

@pytest.fixture
def product(db):
    product = Product.objects.create(
        name="Producto Test",
        price=Decimal("10.00"),
        stock=20
    )
    yield product
    product.stock = 20
    product.save()

@pytest.fixture
def service(db):
    return Service.objects.create(
        name="Servicio Test",
        price=Decimal("15.00")
    )

@pytest.fixture
def cart_product(db, customer, product):
    product.stock = 20
    product.save()

    cart = Cart.objects.create(
        customer=customer,
        product=product,
        quantity=1,
        current_price=product.price
    )
    yield cart

    product.refresh_from_db()
    product.stock = 20
    product.save()

@pytest.fixture
def cart_service(db, customer, service):
    return Cart.objects.create(
        customer=customer,
        service=service,
        quantity=1,
        current_price=service.get_final_price()
    )

# ------------------------------
# CART VIEW TESTS
# ------------------------------

def test_view_cart_contains_items(client, db, customer, cart_product, cart_service):
    client.login(email=customer.email, password="password1234")
    url = reverse("view_cart")
    response = client.get(url)
    assert response.status_code == 200
    items = response.context['items']
    assert any(i.product == cart_product.product for i in items)
    assert any(i.service == cart_service.service for i in items)

def test_view_cart_ajax(client, db, customer, product):
    Cart.objects.create(
        customer=customer,
        product=product,
        quantity=2,
        current_price=product.price
    )

    client.login(email=customer.email, password="password1234")
    url = reverse("view_cart") + "?ajax=1"
    response = client.get(url)
    assert response.status_code == 200
    assert b"Producto Test" in response.content

# ------------------------------
# CART MODIFY TESTS
# ------------------------------

def test_add_product_to_cart_increases_quantity(client, db, customer, product):
    client.login(email=customer.email, password="password1234")
    url = reverse("add_product", args=[product.id])
    response = client.post(url, {"quantity": 2})
    assert response.status_code == 302
    cart_item = Cart.objects.get(customer=customer, product=product)
    assert cart_item.quantity == 2

def test_add_service_to_cart(client, db, customer, service):
    client.login(email=customer.email, password="password1234")
    url = reverse("add_service", args=[service.id])
    response = client.post(url, {"quantity": 1})
    assert response.status_code == 302
    cart_item = Cart.objects.get(customer=customer, service=service)
    assert cart_item.quantity == 1

def test_decrease_product_from_cart(client, db, cart_product):
    client.login(email=cart_product.customer.email, password="password1234")
    product = cart_product.product
    url = reverse("decrease_product_from_cart", args=[product.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Cart.objects.filter(customer=cart_product.customer, product=product).exists()

def test_decrease_service_from_cart(client, db, cart_service):
    client.login(email=cart_service.customer.email, password="password1234")
    url = reverse("decrease_service_from_cart", args=[cart_service.service.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Cart.objects.filter(customer=cart_service.customer, service=cart_service.service).exists()

def test_remove_product_from_cart(client, db, cart_product):
    client.login(email=cart_product.customer.email, password="password1234")
    product = cart_product.product
    url = reverse("remove_product_from_cart", args=[product.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Cart.objects.filter(customer=cart_product.customer, product=product).exists()

def test_remove_service_from_cart(client, db, cart_service):
    client.login(email=cart_service.customer.email, password="password1234")
    url = reverse("remove_service_from_cart", args=[cart_service.service.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Cart.objects.filter(customer=cart_service.customer, service=cart_service.service).exists()

def test_clear_cart(client, db, cart_product, cart_service):
    client.login(email=cart_product.customer.email, password="password1234")
    url = reverse("clear_cart")
    response = client.post(url)
    assert response.status_code == 302
    assert not Cart.objects.filter(customer=cart_product.customer).exists()

# ------------------------------
# CHECKOUT / PAYMENT TESTS
# ------------------------------

def test_checkout_get(client, db, customer, cart_product):
    client.login(email=customer.email, password="password1234")
    url = reverse("checkout")
    response = client.get(url)
    assert response.status_code == 200
    assert "items" in response.context

def test_checkout_post_cod_redirects(client, db, customer, cart_product):
    client.login(email=customer.email, password="password1234")
    session = client.session
    session['checkout_data'] = {
        "delivery_option": "DELIVERY",
        "address": "Calle Falsa 123",
        "city": "Madrid",
        "zip_code": "28001",
        "email": customer.email,
        "payment_method": "contrareembolso",
        "notes": ""
    }
    session.save()
    url = reverse("checkout")
    response = client.post(url, session['checkout_data'])
    assert response.status_code == 302
    assert response.url == reverse("payment_success_cod")

def test_payment_complete_creates_order(client, db, customer, cart_product):
    client.login(email=customer.email, password="password1234")
    session = client.session
    session['checkout_data'] = {
        "delivery_option": "DELIVERY",
        "address": "Calle Falsa 123",
        "city": "Madrid",
        "zip_code": "28001",
        "email": customer.email,
        "payment_method": "tarjeta_credito",
        "notes": "Test note"
    }
    session.save()
    product = cart_product.product
    initial_stock = product.stock 
    url = reverse("payment_complete")
    response = client.post(url, {"payment_method": "tarjeta_credito"})
    assert response.status_code in [200, 302]
    assert Order.objects.filter(customer=customer).exists()
    product.refresh_from_db()
    assert product.stock == initial_stock - cart_product.quantity

def test_payment_success_cod_creates_order(client, db, customer, cart_product):
    client.login(email=customer.email, password="password1234")
    session = client.session
    session['checkout_data'] = {
        "delivery_option": "DELIVERY",
        "address": "Calle Falsa 123",
        "city": "Madrid",
        "zip_code": "28001",
        "email": customer.email,
        "payment_method": "contrareembolso",
        "notes": ""
    }
    session.save()
    product = cart_product.product
    initial_stock = product.stock 
    url = reverse("payment_success_cod")
    response = client.get(url)
    assert response.status_code == 200
    order = Order.objects.get(customer=customer)
    assert order.details.exists()
    assert not Cart.objects.filter(customer=customer).exists()
    product.refresh_from_db()
    assert product.stock == initial_stock - cart_product.quantity

# ------------------------------
# STOCK VALIDATION TESTS
# ------------------------------

def test_payment_complete_fails_when_not_enough_stock(client, db, customer, product):
    """
    Si el producto tiene menos stock que la cantidad del carrito,
    payment_complete_view debe devolver 400 y NO crear pedido.
    """
    client.login(email=customer.email, password="password1234")

    product.stock = 1
    product.save()

    Cart.objects.create(
        customer=customer,
        product=product,
        quantity=5,
        current_price=product.price
    )

    session = client.session
    session['checkout_data'] = {
        "delivery_option": "DELIVERY",
        "address": "Calle Falsa 123",
        "city": "Madrid",
        "zip_code": "28001",
        "email": customer.email,
        "payment_method": "tarjeta_credito",
        "notes": ""
    }
    session.save()

    url = reverse("payment_complete")
    response = client.post(url)

    assert response.status_code == 200
    assert "stock_error.html" in [t.name for t in response.templates]
    assert not Order.objects.filter(customer=customer).exists()


def test_payment_success_cod_fails_when_not_enough_stock(client, db, customer, product):
    """
    Si no hay suficiente stock en COD, debe devolver 400 y NO crear pedido.
    """
    client.login(email=customer.email, password="password1234")

    product.stock = 2
    product.save()

    Cart.objects.create(
        customer=customer,
        product=product,
        quantity=10,
        current_price=product.price
    )

    session = client.session
    session['checkout_data'] = {
        "delivery_option": "DELIVERY",
        "address": "Calle Falsa 123",
        "city": "Madrid",
        "zip_code": "28001",
        "email": customer.email,
        "payment_method": "contrareembolso",
        "notes": ""
    }
    session.save()

    url = reverse("payment_success_cod")
    response = client.get(url)

    assert response.status_code == 200
    assert "stock_error.html" in [t.name for t in response.templates]
    assert not Order.objects.filter(customer=customer).exists()


# ------------------------------
# ORDER LOOKUP
# ------------------------------

def test_order_lookup_invalid(client, db):
    url = reverse("order_lookup")
    response = client.post(url, {"order_public_id": "NOEXISTE"})
    assert response.status_code == 200
    assert "error" in response.context

# ------------------------------
# BUY NOW TESTS
# ------------------------------

def test_buy_now_product_redirects_to_checkout(client, db, customer, product):
    client.login(email=customer.email, password="password1234")

    url = reverse("buy_now_product", args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "items" in response.context

    cart_items = Cart.objects.filter(customer=customer)
    assert cart_items.count() == 1
    assert cart_items.first().product == product


def test_buy_now_service_redirects_to_checkout(client, db, customer, service):
    client.login(email=customer.email, password="password1234")

    url = reverse("buy_now_service", args=[service.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "items" in response.context

    cart_items = Cart.objects.filter(customer=customer)
    assert cart_items.count() == 1
    assert cart_items.first().service == service

