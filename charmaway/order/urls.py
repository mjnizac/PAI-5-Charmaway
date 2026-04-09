from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/product/<int:product_id>/", views.add_product_to_cart, name="add_product"),
    path("cart/add/service/<int:service_id>/", views.add_service_to_cart, name="add_service"),
    path("cart/decrease/product/<int:product_id>/", views.decrease_product_from_cart, name="decrease_product_from_cart"),
    path("cart/decrease/service/<int:service_id>/", views.decrease_service_from_cart, name="decrease_service_from_cart"),
    path("cart/remove/product/<int:product_id>/", views.remove_product_from_cart, name="remove_product_from_cart"),
    path("cart/remove/service/<int:service_id>/", views.remove_service_from_cart, name="remove_service_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/checkout/", views.checkout, name="checkout"),
    path("lookup/", views.order_lookup, name="order_lookup"),
    path("payment-complete/", views.payment_complete_view, name="payment_complete"),
    path("payment-success-cod/", views.payment_success_cod, name="payment_success_cod"),
    path("<str:public_id>/", views.order_detail, name="order_detail"),
    path("buy-now/product/<int:product_id>/", views.buy_now_product, name="buy_now_product"),
    path("buy-now/service/<int:service_id>/", views.buy_now_service, name="buy_now_service"),

    
]

