import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

Customer = get_user_model()


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


# ------------------------------
# REGISTRO
# ------------------------------

@pytest.mark.django_db
def test_register_get(client):
    url = reverse("register")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.django_db
def test_register_post_correct(client, db):#############
    url = reverse("register")

    data = {
        "name": "Ana",
        "surnames": "López Martín",
        "email": "ana@example.com",
        "phone": "+34987654321",
        "address": "Av. Principal 50",
        "city": "Sevilla",
        "zip_code": "41001",
        "password1": "SecurePassword",
        "password2": "SecurePassword",
    }
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse("profile")

    created = Customer.objects.filter(email="ana@example.com").exists()
    assert created

@pytest.mark.django_db
def test_register_post_invalid(client, db):
    url = reverse("register")
    data = {
        "email": "sin_nombre@example.com",
        "password1": "123",
        "password2": "456",
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert response.context["form"].errors


# ------------------------------
# LOGIN
# ------------------------------

@pytest.mark.django_db
def test_login_get(client):
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.django_db
def test_login_post_correct(client, customer):
    url = reverse("login")
    data = {"username": customer.email, "password": "password1234"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("profile")

@pytest.mark.django_db
def test_login_post_invalid(client, customer):
    url = reverse("login")
    data = {"username": customer.email, "password": "incorrecta"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert response.context["form"].errors


# ------------------------------
# LOGOUT
# ------------------------------

@pytest.mark.django_db
def test_logout(client, customer):
    client.login(email=customer.email, password="password1234")
    url = reverse("logout")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("login")


# ------------------------------
# PROFILE VIEW
# ------------------------------

@pytest.mark.django_db
def test_profile_requires_login(client): #############
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_profile_logged_in(client, customer):
    client.login(email=customer.email, password="password1234")
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["customer"].email == customer.email


# ------------------------------
# PROFILE EDIT
# ------------------------------

@pytest.mark.django_db
def test_profile_edit_get(client, customer):
    client.login(email=customer.email, password="password1234")
    url = reverse("profile_edit")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.django_db
def test_profile_edit_post_correct(client, customer):
    client.login(email=customer.email, password="password1234")
    url = reverse("profile_edit")

    data = {
        "name": "NuevoNombre",
        "surnames": customer.surnames,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "zip_code": customer.zip_code,
        "prefered_payment_method": customer.prefered_payment_method,
    }

    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("profile")

    customer.refresh_from_db()
    assert customer.name == "NuevoNombre"

@pytest.mark.django_db
def test_profile_edit_post_invalid(client, customer):
    client.login(email=customer.email, password="password1234")
    url = reverse("profile_edit")

    data = {
        "name": "",
        "surnames": customer.surnames,
        "email": customer.email,
        "phone": "teléfono-malo",
        "address": customer.address,
        "city": customer.city,
        "zip_code": customer.zip_code,
    }

    response = client.post(url, data)
    assert response.status_code == 200
    assert response.context["form"].errors
