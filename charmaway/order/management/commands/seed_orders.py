from django.core.management.base import BaseCommand
from customer.models import Customer
from catalog.models import Product
from services.models import Service
from order.models import Cart, Order, OrderDetail, OrderStatus
from decimal import Decimal
import shortuuid

class Command(BaseCommand):
    help = 'Crea pedidos y carritos fijos para pruebas con todos los clientes'

    def handle(self, *args, **options):
        def set_shipping(order, subtotal, delivery_option):
            if delivery_option == "PICKUP":
                order.shipping_cost = Decimal("0.00")
            else:
                order.shipping_cost = Decimal('2.99') if subtotal < Decimal('20.00') else Decimal('0.00')
            order.final_price = subtotal + order.shipping_cost

        customers = list(Customer.objects.all()[:7])

        products = list(Product.objects.filter(is_available=True)[:5])
        services = list(Service.objects.filter(is_available=True)[:5])
        p1, p2, p3, p4, p5 = products
        s1, s2, s3, s4, s5 = services
        admin, user, c1, c2, c3, c4, c5 = customers

        Cart.objects.all().delete()
        OrderDetail.objects.all().delete()
        Order.objects.all().delete()

        Cart.objects.create(customer=admin, product=p1, quantity=1, current_price=p1.price)
        Cart.objects.create(customer=user, product=p2, quantity=2, current_price=p2.price)
        Cart.objects.create(customer=c1, product=p3, quantity=1, current_price=p3.price)
        Cart.objects.create(customer=c2, product=p4, quantity=2, current_price=p4.price)
        Cart.objects.create(customer=c3, product=p5, quantity=1, current_price=p5.price)
        Cart.objects.create(customer=c4, product=p1, quantity=3, current_price=p1.price)
        Cart.objects.create(customer=c5, product=p2, quantity=2, current_price=p2.price)

        Cart.objects.create(customer=admin, service=s1, quantity=1, current_price=s1.price)
        Cart.objects.create(customer=user, service=s2, quantity=1, current_price=s2.price)
        Cart.objects.create(customer=c1, service=s3, quantity=2, current_price=s3.price)
        Cart.objects.create(customer=c2, service=s4, quantity=1, current_price=s4.price)
        Cart.objects.create(customer=c3, service=s5, quantity=1, current_price=s5.price)

        self.stdout.write(self.style.SUCCESS('Carritos fijos creados'))

        o1 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=admin, email=admin.email,
            address=admin.address, city=admin.city, zip_code=admin.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.PROCESSING,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o1, product=p1, quantity=1, unit_price=p1.price, subtotal=p1.price)
        OrderDetail.objects.create(order=o1, service=s1, quantity=1, unit_price=s1.price, subtotal=s1.price)
        o1.subtotal = p1.price + s1.price
        set_shipping(o1, o1.subtotal, o1.delivery_option)
        o1.save()

        o2 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=user, email=user.email,
            address=user.address, city=user.city, zip_code=user.zip_code,
            payment_method='contrareembolso', status=OrderStatus.SHIPPED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o2, product=p2, quantity=2, unit_price=p2.price, subtotal=p2.price*2)
        OrderDetail.objects.create(order=o2, service=s2, quantity=1, unit_price=s2.price, subtotal=s2.price)
        o2.subtotal = p2.price*2 + s2.price
        set_shipping(o2, o2.subtotal, o2.delivery_option)
        o2.save()

        o3 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c1, email=c1.email,
            address=c1.address, city=c1.city, zip_code=c1.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.DELIVERED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o3, product=p1, quantity=1, unit_price=p1.price, subtotal=p1.price)
        OrderDetail.objects.create(order=o3, product=p3, quantity=1, unit_price=p3.price, subtotal=p3.price)
        OrderDetail.objects.create(order=o3, service=s3, quantity=1, unit_price=s3.price, subtotal=s3.price)
        o3.subtotal = p1.price + p3.price + s3.price
        set_shipping(o3, o3.subtotal, o3.delivery_option)
        o3.save()

        o4 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c1, email=c1.email,
            address='Calle Mayor 12', city=c1.city, zip_code=c1.zip_code,
            payment_method='contrareembolso', status=OrderStatus.CANCELLED,
            delivery_option="PICKUP"
        )
        OrderDetail.objects.create(order=o4, product=p2, quantity=1, unit_price=p2.price, subtotal=p2.price)
        OrderDetail.objects.create(order=o4, product=p4, quantity=1, unit_price=p4.price, subtotal=p4.price)
        OrderDetail.objects.create(order=o4, service=s4, quantity=1, unit_price=s4.price, subtotal=s4.price)
        o4.subtotal = p2.price + p4.price + s4.price
        set_shipping(o4, o4.subtotal, o4.delivery_option)
        o4.save()

        o_extra1 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c1, email=c1.email,
            address='Av. Nueva 45', city=c1.city, zip_code=c1.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.PROCESSING,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o_extra1, product=p5, quantity=2, unit_price=p5.price, subtotal=p5.price*2)
        OrderDetail.objects.create(order=o_extra1, service=s5, quantity=1, unit_price=s5.price, subtotal=s5.price)
        o_extra1.subtotal = p5.price*2 + s5.price
        set_shipping(o_extra1, o_extra1.subtotal, o_extra1.delivery_option)
        o_extra1.save()

        o_extra2 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c1, email=c1.email,
            address='Calle del Río 10', city=c1.city, zip_code=c1.zip_code,
            payment_method='contrareembolso', status=OrderStatus.SHIPPED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o_extra2, product=p3, quantity=1, unit_price=p3.price, subtotal=p3.price)
        OrderDetail.objects.create(order=o_extra2, product=p4, quantity=2, unit_price=p4.price, subtotal=p4.price*2)
        OrderDetail.objects.create(order=o_extra2, service=s2, quantity=1, unit_price=s2.price, subtotal=s2.price)
        o_extra2.subtotal = p3.price + p4.price*2 + s2.price
        set_shipping(o_extra2, o_extra2.subtotal, o_extra2.delivery_option)
        o_extra2.save()

        o5 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c2, email=c2.email,
            address=c2.address, city=c2.city, zip_code=c2.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.DELIVERED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o5, product=p1, quantity=2, unit_price=p1.price, subtotal=p1.price*2)
        OrderDetail.objects.create(order=o5, service=s1, quantity=1, unit_price=s1.price, subtotal=s1.price)
        o5.subtotal = p1.price*2 + s1.price
        set_shipping(o5, o5.subtotal, o5.delivery_option)
        o5.save()

        o6 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c2, email=c2.email,
            address='Avenida Reina Mercedes 130', city=c2.city, zip_code=c2.zip_code,
            payment_method='contrareembolso', status=OrderStatus.PROCESSING,
            delivery_option="PICKUP"
        )
        OrderDetail.objects.create(order=o6, product=p3, quantity=1, unit_price=p3.price, subtotal=p3.price)
        OrderDetail.objects.create(order=o6, product=p4, quantity=1, unit_price=p4.price, subtotal=p4.price)
        OrderDetail.objects.create(order=o6, service=s4, quantity=2, unit_price=s4.price, subtotal=s4.price*2)
        o6.subtotal = p3.price + p4.price + s4.price*2
        set_shipping(o6, o6.subtotal, o6.delivery_option)
        o6.save()

        o7 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c3, email=c3.email,
            address=c3.address, city=c3.city, zip_code=c3.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.CANCELLED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o7, product=p1, quantity=1, unit_price=p1.price, subtotal=p1.price)
        OrderDetail.objects.create(order=o7, service=s3, quantity=1, unit_price=s3.price, subtotal=s3.price)
        o7.subtotal = p1.price + s3.price
        set_shipping(o7, o7.subtotal, o7.delivery_option)
        o7.save()

        o8 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c3, email=c3.email,
            address='Paseo de la Luna 18', city=c3.city, zip_code=c3.zip_code,
            payment_method='contrareembolso', status=OrderStatus.SHIPPED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o8, product=p2, quantity=2, unit_price=p2.price, subtotal=p2.price*2)
        OrderDetail.objects.create(order=o8, service=s5, quantity=1, unit_price=s5.price, subtotal=s5.price)
        o8.subtotal = p2.price*2 + s5.price
        set_shipping(o8, o8.subtotal, o8.delivery_option)
        o8.save()

        o9 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c4, email=c4.email,
            address=c4.address, city=c4.city, zip_code=c4.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.PROCESSING,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o9, product=p3, quantity=1, unit_price=p3.price, subtotal=p3.price)
        OrderDetail.objects.create(order=o9, service=s2, quantity=1, unit_price=s2.price, subtotal=s2.price)
        o9.subtotal = p3.price + s2.price
        set_shipping(o9, o9.subtotal, o9.delivery_option)
        o9.save()

        o10 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c4, email=c4.email,
            address='Ronda del Río 25', city=c4.city, zip_code=c4.zip_code,
            payment_method='contrareembolso', status=OrderStatus.DELIVERED,
            delivery_option="PICKUP"
        )
        OrderDetail.objects.create(order=o10, product=p4, quantity=1, unit_price=p4.price, subtotal=p4.price)
        OrderDetail.objects.create(order=o10, product=p5, quantity=1, unit_price=p5.price, subtotal=p5.price)
        OrderDetail.objects.create(order=o10, service=s4, quantity=1, unit_price=s4.price, subtotal=s4.price)
        o10.subtotal = p4.price + p5.price + s4.price
        set_shipping(o10, o10.subtotal, o10.delivery_option)
        o10.save()

        o11 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c5, email=c5.email,
            address=c5.address, city=c5.city, zip_code=c5.zip_code,
            payment_method='tarjeta_credito', status=OrderStatus.PROCESSING,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o11, product=p1, quantity=1, unit_price=p1.price, subtotal=p1.price)
        OrderDetail.objects.create(order=o11, product=p5, quantity=1, unit_price=p5.price, subtotal=p5.price)
        OrderDetail.objects.create(order=o11, service=s1, quantity=1, unit_price=s1.price, subtotal=s1.price)
        o11.subtotal = p1.price + p5.price + s1.price
        set_shipping(o11, o11.subtotal, o11.delivery_option)
        o11.save()

        o12 = Order.objects.create(
            public_id=shortuuid.uuid()[:12], customer=c5, email=c5.email,
            address='Calle del Sol 105', city=c5.city, zip_code=c5.zip_code,
            payment_method='contrareembolso', status=OrderStatus.SHIPPED,
            delivery_option="DELIVERY"
        )
        OrderDetail.objects.create(order=o12, product=p2, quantity=2, unit_price=p2.price, subtotal=p2.price*2)
        OrderDetail.objects.create(order=o12, service=s3, quantity=1, unit_price=s3.price, subtotal=s3.price)
        o12.subtotal = p2.price*2 + s3.price
        set_shipping(o12, o12.subtotal, o12.delivery_option)
        o12.save()

        self.stdout.write(self.style.SUCCESS('✔ Pedidos y carritos fijos creados con métodos de envío variados y servicios asociados'))
