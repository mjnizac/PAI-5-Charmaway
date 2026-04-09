from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.services_catalog, name='services_catalog'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
]
