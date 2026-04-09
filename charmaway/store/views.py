from django.shortcuts import render
from catalog.models import Product, Category, Brand, Department

def home(request):
    # Exclude service departments
    service_dept_names = ['Beauty Academy', 'Premium Services', 'Club Exclusivo']

    # Get featured products (exclude service departments)
    featured_products = Product.objects.exclude(
        category__department__name__in=service_dept_names
    ).filter(
        is_available=True,
        is_featured=True
    ).select_related('brand', 'category').prefetch_related('images')[:8]

    # Get all departments except service departments
    departments = Department.objects.exclude(name__in=service_dept_names).order_by('order_position', 'name')

    context = {
        'featured_products': featured_products,
        'departments': departments,
    }

    return render(request, 'store/home.html', context)

def about(request):
    return render(request, 'store/about.html')