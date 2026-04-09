from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Department


def catalog(request):
    """Display catalog with all products, with optional filtering."""
    # Exclude products from the Services department
    products = Product.objects.exclude(category__department__name='Servicios').select_related('brand', 'category', 'category__department').prefetch_related('images')

    # Get filter parameters
    department_id = request.GET.get('department')
    category_id = request.GET.get('category')
    selected_brands = request.GET.getlist('brand')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'name')
    per_page = request.GET.get('per_page', '24')

    # Filter out empty strings from selected_brands list
    selected_brands = [b for b in selected_brands if b and b.strip()]

    # If no brands in list, check for single brand parameter
    if not selected_brands:
        single_brand = request.GET.get('brand')
        if single_brand and single_brand.strip():
            selected_brands = [single_brand]

    # Apply department filter first
    if department_id and department_id.strip():
        products = products.filter(category__department_id=department_id)

    # Apply category filter (only if values are not empty)
    if category_id and category_id.strip():
        products = products.filter(category_id=category_id)

    # Handle brand filter
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

    if search_query and search_query.strip():
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(category__department__name__icontains=search_query)
        )

    # Apply sorting
    sort_options = {
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price'
    }
    products = products.order_by(sort_options.get(sort_by, 'name'))

    # Pagination
    try:
        items_per_page = int(per_page)
        if items_per_page not in [24, 36, 48]:
            items_per_page = 24
    except (ValueError, TypeError):
        items_per_page = 24

    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get selected department if any
    selected_department = None
    if department_id and department_id.strip():
        selected_department = Department.objects.filter(id=department_id).first()

    # Get categories for the selected department (or all if no department selected)
    # Exclude categories from Services department
    if selected_department:
        categories = Category.objects.filter(department=selected_department).exclude(department__name='Servicios').order_by('order_position', 'name')
    else:
        categories = Category.objects.exclude(department__name='Servicios').order_by('order_position', 'name')

    # Get all brands that have products (before brand filtering)
    # Get base queryset without brand filter for brand list
    # Exclude products from Services department
    brands_queryset = Product.objects.exclude(category__department__name='Servicios')
    if department_id and department_id.strip():
        brands_queryset = brands_queryset.filter(category__department_id=department_id)
    if category_id and category_id.strip():
        brands_queryset = brands_queryset.filter(category_id=category_id)
    if search_query and search_query.strip():
        brands_queryset = brands_queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(category__department__name__icontains=search_query)
        )

    brand_ids = brands_queryset.values_list('brand_id', flat=True).distinct()
    brands = Brand.objects.filter(id__in=brand_ids).order_by('name')

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'selected_department': department_id,
        'selected_category': category_id,
        'selected_brands': selected_brands,
        'search_query': search_query,
        'sort_by': sort_by,
        'per_page': per_page,
        'department_obj': selected_department,
    }

    return render(request, 'catalog/catalog.html', context)


def product_detail(request, product_id):
    """Display detailed information about a specific product."""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('images', 'sizes'),
        id=product_id
    )

    # Get main image or first image
    main_image = product.images.filter(is_main=True).first()
    if not main_image:
        main_image = product.images.first()

    # Get all images
    images = product.images.all().order_by('order_position')

    # Get available sizes
    sizes = product.sizes.all().order_by('size')

    context = {
        'product': product,
        'main_image': main_image,
        'images': images,
        'sizes': sizes,
    }

    return render(request, 'catalog/product_detail.html', context)
