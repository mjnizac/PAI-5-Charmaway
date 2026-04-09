from decimal import Decimal
from django.db import models
from django.utils import timezone
from customer.models import Customer
from catalog.models import Product
from services.models import Service
import shortuuid


class OrderStatus(models.TextChoices):
    PROCESSING = "PROCESSING", "Procesándose"
    SHIPPED = "SHIPPED", "Enviado"
    DELIVERED = "DELIVERED", "Entregado"
    CANCELLED = "CANCELLED", "Cancelado"

class DeliveryOption(models.TextChoices):
    DELIVERY = "DELIVERY", "Envío"
    PICKUP = "PICK_UP", "Recogida en tienda"
    
def generate_unique_public_id():
    while True:
        pid = shortuuid.uuid()[:12]
        if not Order.objects.filter(public_id=pid).exists():
            return pid

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    public_id = models.CharField(
        max_length=12,
        default=generate_unique_public_id,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )

    email = models.EmailField(null=True)

    created_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING
    )

    delivery_option = models.CharField(
        max_length=20,
        choices=DeliveryOption.choices,
        default=DeliveryOption.DELIVERY
    )

    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    def change_status(self, new_status):
        self.status = new_status
        self.save()

    def calculate_total(self):
        details = self.details.all()
        self.subtotal = sum(d.subtotal for d in details)
        self.final_price = Decimal(self.subtotal) + Decimal(self.shipping_cost)
        self.save()

    def cancel(self):
        self.status = OrderStatus.CANCELLED
        self.save()

    def get_details(self):
        return self.details.all()

    def __str__(self):
        customer_name = self.customer.name if self.customer else "Anonymous"
        return f"Order #{self.order_id} - {customer_name}"


class OrderDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="details"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        null=True, blank=True
    )

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_subtotal(self):
        self.subtotal = self.unit_price * self.quantity
        self.save()

    def __str__(self):
        return f"{self.quantity} x {self.product}"


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True
    )

    session_key = models.CharField(max_length=40, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def add_product(self, amount=1):
        self.quantity += amount
        self.save()

    def update_quantity(self, quantity):
        self.quantity = max(1, quantity)
        self.save()

    def remove_product(self):
        self.delete()

    @staticmethod
    def clear_cart(user_or_session):
        if isinstance(user_or_session, Customer):
            Cart.objects.filter(customer=user_or_session).delete()
        else:
            Cart.objects.filter(session_key=user_or_session).delete()

    @staticmethod
    def calculate_total(user_or_session):
        if isinstance(user_or_session, Customer):
            items = Cart.objects.filter(customer=user_or_session)
        else:
            items = Cart.objects.filter(session_key=user_or_session)

        return sum(item.current_price * item.quantity for item in items)

    def __str__(self):
        owner = self.customer.name if self.customer else f"Session {self.session_key}"
        return f"{self.quantity} x {self.product} (Owner: {owner})"
