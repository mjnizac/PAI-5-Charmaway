# payment/urls.py
from django.urls import path
from . import views

app_name = 'payment' 

urlpatterns = [

    path('checkout/', views.pagina_de_pago, name='checkout'),

    path('create-payment-intent/', views.crear_intento_de_pago, name='create_payment_intent'),

    path('webhook/', views.stripe_webhook, name='stripe_webhook')
]