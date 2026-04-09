from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from order.models import Order
from .forms import CustomerRegisterForm, CustomerLoginForm, CustomerUpdateForm
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator


def register(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomerRegisterForm()
    return render(request, 'customer/register.html', {'form': form})

def login_(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        print(form)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomerLoginForm()
    return render(request, 'customer/login.html', {'form': form})

def logout_(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    customer = request.user
    orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]

    return render(request, "customer/profile.html", {
        "customer": customer,
        "orders": orders
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomerUpdateForm(instance=request.user)
    return render(request, 'customer/profile_edit.html', {'form': form})

@login_required
def all_orders(request):
    customer = request.user
    orders_list = Order.objects.filter(customer=customer).order_by('-created_at')

    paginator = Paginator(orders_list, 7)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "customer/orders.html", {
        "page_obj": page_obj
    })
