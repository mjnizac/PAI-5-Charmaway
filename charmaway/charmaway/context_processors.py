from django.db.models import Sum
from order.models import Cart
from catalog.models import Department, Category, Brand

def cart_item_count(request):
    session_key = request.session.session_key

    if request.user.is_authenticated:
        queryset = Cart.objects.filter(customer=request.user)
    elif session_key is None:
        return {"cart_item_count": 0}
    else:
        queryset = Cart.objects.filter(session_key=session_key)

    total_items = queryset.aggregate(total=Sum("quantity"))["total"] or 0

    return {"cart_item_count": total_items}

def search_filters(request):
    """Provide departments, categories and brands for search filters in all templates"""
    # Check if we're in the services view
    is_services_view = request.path.startswith('/services/')

    if is_services_view:
        # For services view, only show service departments and their categories
        service_dept_names = ['Beauty Academy', 'Premium Services', 'Club Exclusivo']
        departments = Department.objects.filter(name__in=service_dept_names).order_by('order_position')
        categories = Category.objects.filter(department__name__in=service_dept_names).select_related('department').order_by('department__order_position', 'order_position')
        brands = Brand.objects.none()  # No brands in services
    else:
        # For other views, exclude service departments
        service_dept_names = ['Beauty Academy', 'Premium Services', 'Club Exclusivo']
        departments = Department.objects.exclude(name__in=service_dept_names).order_by('order_position', 'name')
        categories = Category.objects.none()  # Categories not needed in header for products
        brands = Brand.objects.all().order_by('name')

    return {
        "all_departments": departments,
        "all_categories": categories,
        "all_brands": brands,
        "is_services_view": is_services_view
    }
