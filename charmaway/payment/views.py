from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import stripe

from order.models import Order, Cart, OrderStatus 

def pagina_de_pago(request):
    """
    Muestra la página de pago de Stripe.
    """
    try:
        total = request.session.get('checkout_total')
        context = {
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'order_total': total
        }
        return render(request, 'payment/checkout.html', context)
    
    except Order.DoesNotExist:
        return redirect('view_cart')


def crear_intento_de_pago(request):
    """
    Crea el PaymentIntent con el monto del pedido.
    """
    if request.method == 'POST':
        try:
            total = request.session.get('checkout_total')
            if total is None:
                return JsonResponse({'error': 'No hay total para pagar'}, status=403)

            monto_en_centavos = int(Decimal(total) * 100)
            if monto_en_centavos <= 0:
                return JsonResponse({'error': 'El monto debe ser positivo'}, status=400)

            if monto_en_centavos <= 0:
                 return JsonResponse({'error': 'El monto debe ser positivo'}, status=400)

            intent = stripe.PaymentIntent.create(
                amount=monto_en_centavos,
                currency='eur',
                automatic_payment_methods={'enabled': True},
            )
            
            return JsonResponse({'clientSecret': intent.client_secret})
        
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
        except Exception as e:
            print(f"Error al crear PaymentIntent: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        try:
            order = Order.objects.get(order_id=order_id)
            
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.PROCESSING 
                order.save()
            
                Cart.clear_cart(order.customer)
            
            print(f"Éxito: Pedido {order_id} actualizado a PROCESSING.")

        except Order.DoesNotExist:
            print(f"Error en Webhook: Pedido {order_id} no encontrado.")
            return HttpResponse(status=404)

    elif event['type'] == 'payment_intent.payment_failed':
        print(f"Webhook: Pago fallido para pedido {payment_intent['metadata'].get('order_id')}.")

    return HttpResponse(status=200)
