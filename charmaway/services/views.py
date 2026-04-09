from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Service, ServiceCategory
from catalog.models import Category, Department


def services_catalog(request):
    """Display services catalog with filtering by department and category."""
    services = Service.objects.all().select_related('category', 'category__department')

    # Get filter parameters
    department_id = request.GET.get('department')
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'name')
    per_page = request.GET.get('per_page', '24')

    # Apply department filter
    if department_id and department_id.strip():
        services = services.filter(category__department_id=department_id)

    # Apply category filter
    if category_id and category_id.strip():
        services = services.filter(category_id=category_id)

    # Apply search filter (only within service departments)
    if search_query and search_query.strip():
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(category__department__name__icontains=search_query)
        )

    # Apply sorting
    sort_options = {
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price'
    }
    services = services.order_by(sort_options.get(sort_by, 'name'))

    # Pagination
    try:
        items_per_page = int(per_page)
        if items_per_page not in [24, 36, 48]:
            items_per_page = 24
    except (ValueError, TypeError):
        items_per_page = 24

    paginator = Paginator(services, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get all service departments and categories
    service_dept_names = ['Beauty Academy', 'Premium Services', 'Club Exclusivo']
    departments = Department.objects.filter(name__in=service_dept_names).order_by('order_position')

    # Get selected department object if department_id is provided
    selected_department_obj = None
    if department_id and department_id.strip():
        try:
            selected_department_obj = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            pass

    # Filter categories based on selected department (like catalog does)
    if department_id and department_id.strip():
        categories = Category.objects.filter(department_id=department_id).select_related('department').order_by('order_position')
    else:
        categories = Category.objects.filter(department__name__in=service_dept_names).select_related('department').order_by('department__order_position', 'order_position')

    context = {
        'services': page_obj,
        'page_obj': page_obj,
        'departments': departments,
        'categories': categories,
        'selected_department': department_id,
        'selected_department_obj': selected_department_obj,
        'selected_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    return render(request, 'services/services_catalog.html', context)


def service_detail(request, service_id):
    """Display detailed information about a specific service."""
    service = get_object_or_404(
        Service.objects.select_related('category'),
        id=service_id
    )

    context = {
        'service': service,
    }

    return render(request, 'services/service_detail.html', context)
