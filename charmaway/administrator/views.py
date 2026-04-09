from django.shortcuts import render, get_object_or_404, redirect
from catalog.models import Product
from services.models import Service
from customer.models import Customer
from order.models import Order
from .forms import ProductForm, ImageFormSet, SizeFormSet, CustomerBaseForm, CustomerCreateForm, OrderStatusForm, ServiceForm
from .decorators import admin_required
from django.contrib import messages
from django.db.models import Q, CharField, Value, Sum
from django.db.models.functions import Concat
from django.db.models.deletion import ProtectedError

@admin_required
def admin_dashboard(request):
    
    total_products = Product.objects.exclude(category__department__name='Servicios').count()
    total_clients = Customer.objects.count()
    total_orders = Order.objects.count()
    total_services = Service.objects.count()
    total_revenue = Order.objects.filter(status='DELIVERED').aggregate(total_revenue=Sum('final_price'))['total_revenue'] or 0
    total_lost = Order.objects.filter(status='CANCELLED').aggregate(total_lost=Sum('final_price'))['total_lost'] or 0
    average_order_value = Order.objects.filter(status='DELIVERED').aggregate(average_value=Sum('final_price') / Sum(1))['average_value'] or 0
    total_expected_revenue = Order.objects.filter(status__in=['PROCESSING', 'SHIPPED','DELIVERED']).aggregate(expected_revenue=Sum('final_price'))['expected_revenue'] or 0
    
    context = {
        'total_products': total_products,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'total_services': total_services,
        'total_revenue': total_revenue,
        'total_lost': total_lost,
        'average_order_value': average_order_value,
        'total_expected_revenue': total_expected_revenue
    }
    return render(request, 'administrator/admin_dashboard.html', context)

@admin_required
def product_list(request):
    products = Product.objects.exclude(
            category__department__name='Servicios'
        ).select_related('brand', 'category')
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    context = {
        'products': products
    }
    return render(request, 'administrator/product/product_list.html', context)

@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_formset = ImageFormSet(request.POST)
        size_formset = SizeFormSet(request.POST)
        if form.is_valid() and image_formset.is_valid() and size_formset.is_valid():
            product = form.save()
            image_formset.instance = product
            image_formset.save()
            size_formset.instance = product
            size_formset.save()
            return redirect('administrator:product_list')
    else:
        form = ProductForm()
        image_formset = ImageFormSet()
        size_formset = SizeFormSet()
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'size_formset': size_formset
    }
    
    return render(request, 'administrator/product/product_edit.html', context)

@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        image_formset = ImageFormSet(request.POST, instance=product)
        size_formset = SizeFormSet(request.POST, instance=product)
        if form.is_valid() and image_formset.is_valid() and size_formset.is_valid():
            main_stock = form.cleaned_data.get('stock', 0)
            sizes_stock_sum = 0
            has_sizes = False
            
            for size_form in size_formset:
                if size_form.cleaned_data and not size_form.cleaned_data.get('DELETE'):
                    sizes_stock_sum += size_form.cleaned_data.get('stock', 0)
                    has_sizes = True
            
            if has_sizes and main_stock != sizes_stock_sum:
                form.add_error('stock', f"El Stock Total ({main_stock}) no coincide con la suma de las tallas ({sizes_stock_sum}).")                
                context = {
                    'form': form,
                    'image_formset': image_formset,
                    'size_formset': size_formset,
                    'product': product
                }
                return render(request, 'administrator/product/product_edit.html', context)

            form.save()
            image_formset.save()
            size_formset.save()
            return redirect('administrator:product_list')
    else:
        form = ProductForm(instance=product)
        image_formset = ImageFormSet(instance=product)
        size_formset = SizeFormSet(instance=product)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'size_formset': size_formset,
        'product': product
    }
    
    return render(request, 'administrator/product/product_edit.html', context)

@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    try:
        product.delete()
        messages.success(request, "El producto ha sido eliminado correctamente.")
        
    except ProtectedError as e:
        objetos_bloqueantes = e.args[1]
        ids_pedidos = set(detalle.order.order_id for detalle in objetos_bloqueantes)
        lista_pedidos_str = ", ".join(str(id) for id in ids_pedidos)
        mensaje_error = (
            f"⚠️ No se puede eliminar '{product.name}'. "
            f"Aparece en los siguientes Pedidos (IDs): {lista_pedidos_str} ."
        )
        
        messages.error(request, mensaje_error)
        
    return redirect('administrator:product_list')

@admin_required
def service_list(request):
    services = Service.objects.all().order_by('name')
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    context = {
        'services': services
    }
    return render(request, 'administrator/service/service_list.html', context)

@admin_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('administrator:service_list')
    else:
        form = ServiceForm()
    context = {
        'form': form
    }
    return render(request, 'administrator/service/service_edit.html', context)

@admin_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('administrator:service_list')
    else:
        form = ServiceForm(instance=service)
    context = {
        'form': form,
        'service': service
    }
    return render(request, 'administrator/service/service_edit.html', context)

@admin_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    try:
        service.delete()
        messages.success(request, "El servicio ha sido eliminado correctamente.")
    except ProtectedError as e:
        objetos_bloqueantes = e.args[1]
        ids_pedidos = set(detalle.order.order_id for detalle in objetos_bloqueantes)
        lista_pedidos_str = ", ".join(str(id) for id in ids_pedidos)
        mensaje_error = (
            f"⚠️ No se puede eliminar '{service.name}'. "
            f"Aparece en los siguientes Pedidos (IDs): {lista_pedidos_str} ."
        )
        
        messages.error(request, mensaje_error)
    return redirect('administrator:service_list')

@admin_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-is_superuser')
    query = request.GET.get('q')
    if query:
        customers = customers.annotate(
            search_name=Concat(
                'name', 
                Value(' '), 
                'surnames',
                output_field=CharField()
            )
        ).filter(
            Q(email__icontains=query) |
            Q(search_name__icontains=query)
        ).distinct()
    context = {
        'customers': customers
    }
    return render(request, 'administrator/customer/customer_list.html', context)

@admin_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerBaseForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('administrator:customer_list')
    else:
        form = CustomerBaseForm(instance=customer)

    context = {
        'form': form,
        'customer': customer
    }
    return render(request, 'administrator/customer/customer_edit.html', context)

@admin_required
def customer_delete(request, pk):
    if request.user.pk == pk:
        return redirect('administrator:customer_list')
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('administrator:customer_list')

@admin_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('administrator:customer_list')
    else:
        form = CustomerCreateForm()
    context = {
        'form': form
    }
    return render(request, 'administrator/customer/customer_edit.html', context)

@admin_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at').select_related('customer')
    query = request.GET.get('q')
    if query:
        status_mapping = {
            'procesando': 'PROCESSING',
            'enviado': 'SHIPPED',
            'entregado': 'DELIVERED',
            'cancelado': 'CANCELLED',
        }
        matching_statuses = []
        for es_term, db_value in status_mapping.items():
            if query.lower() in es_term:
                matching_statuses.append(db_value)
        search_filters = (
            Q(public_id__icontains=query) |
            Q(email__icontains=query) |
            Q(search_name__icontains=query)
        )
        if matching_statuses:
            search_filters |= Q(status__in=matching_statuses)
        orders = orders.annotate(
            search_name=Concat(
                'customer__name', 
                Value(' '), 
                'customer__surnames',
                output_field=CharField()
            ),
        ).filter(
            search_filters
        ).distinct()
    context = {
        'orders': orders
    }
    return render(request, 'administrator/order/order_list.html', context)

@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('administrator:order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)

    context = {
        'form': form,
        'order': order,
        'details': order.details.filter(product__isnull=False).select_related('product'),
        'services': order.details.filter(service__isnull=False).select_related('service'),
    }
    return render(request, 'administrator/order/order_detail.html', context)