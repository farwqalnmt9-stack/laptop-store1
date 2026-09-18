from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import ReviewForm, CheckoutForm, LaptopAdminForm
from .models import Brand, Category, Laptop, Wishlist, Order, OrderItem


def home(request):
    featured = Laptop.objects.filter(is_active=True, is_featured=True)[:8]
    deals = Laptop.objects.filter(is_active=True, discount_price__isnull=False)[:4]
    categories = Category.objects.all()
    new_arrivals = Laptop.objects.filter(is_active=True).order_by('-created_at')[:8]
    showcase = list(featured[:5]) or list(new_arrivals[:5])
    library = list(featured[:8]) or list(new_arrivals[:8])
    return render(request, 'store/home.html', {
        'featured': featured,
        'deals': deals,
        'categories': categories,
        'new_arrivals': new_arrivals,
        'showcase': showcase,
        'library': library,
    })


def product_list(request):
    laptops = Laptop.objects.filter(is_active=True)

    q = request.GET.get('q', '').strip()
    if q:
        laptops = laptops.filter(
            Q(name__icontains=q) | Q(cpu__icontains=q) | Q(gpu__icontains=q) | Q(brand__name__icontains=q)
        )

    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        laptops = laptops.filter(brand__slug__in=brand_slugs)

    category_slug = request.GET.get('category')
    if category_slug:
        laptops = laptops.filter(category__slug=category_slug)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try:
        if min_price:
            laptops = laptops.filter(price__gte=Decimal(min_price))
        if max_price:
            laptops = laptops.filter(price__lte=Decimal(max_price))
    except InvalidOperation:
        pass

    min_ram = request.GET.get('min_ram')
    if min_ram:
        laptops = laptops.filter(ram_gb__gte=min_ram)

    storage_type = request.GET.get('storage_type')
    if storage_type:
        laptops = laptops.filter(storage_type=storage_type)

    in_stock = request.GET.get('in_stock')
    if in_stock:
        laptops = laptops.filter(stock__gt=0)

    sort = request.GET.get('sort', '-created_at')
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'name': 'name',
    }
    laptops = laptops.order_by(sort_map.get(sort, '-created_at'))

    context = {
        'laptops': laptops,
        'brands': Brand.objects.all(),
        'categories': Category.objects.all(),
        'selected_brands': brand_slugs,
        'selected_category': category_slug,
        'query': q,
        'sort': sort,
        'result_count': laptops.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    laptop = get_object_or_404(Laptop, slug=slug, is_active=True)
    related = Laptop.objects.filter(category=laptop.category, is_active=True).exclude(pk=laptop.pk)[:4]
    review_form = ReviewForm()
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, laptop=laptop).exists()

    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.info(request, 'Sign in to leave a review.')
            return redirect('accounts:login')
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review, created = laptop.reviews.update_or_create(
                user=request.user,
                defaults={
                    'rating': review_form.cleaned_data['rating'],
                    'title': review_form.cleaned_data['title'],
                    'comment': review_form.cleaned_data['comment'],
                }
            )
            messages.success(request, 'Thanks — your review is posted.')
            return redirect('store:product_detail', slug=slug)

    compare_ids = request.session.get('compare', [])

    return render(request, 'store/product_detail.html', {
        'laptop': laptop,
        'related': related,
        'review_form': review_form,
        'is_wishlisted': is_wishlisted,
        'in_compare': laptop.id in compare_ids,
    })


@require_POST
def cart_add(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id, is_active=True)
    cart = Cart(request)
    if not laptop.in_stock:
        messages.error(request, f'{laptop.name} is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))
    cart.add(laptop)
    messages.success(request, f'Added {laptop.name} to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'store:cart'))


@require_POST
def cart_update(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id)
    cart = Cart(request)
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1
    if qty <= 0:
        cart.remove(laptop)
    else:
        cart.add(laptop, quantity=qty, replace=True)
    return redirect('store:cart')


@require_POST
def cart_remove(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id)
    cart = Cart(request)
    cart.remove(laptop)
    messages.info(request, f'Removed {laptop.name} from cart.')
    return redirect('store:cart')


def cart_view(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, 'Your cart is empty.')
        return redirect('store:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.total
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    laptop=item['laptop'],
                    laptop_name=item['laptop'].name,
                    unit_price=item['unit_price'],
                    quantity=item['quantity'],
                )
                item['laptop'].stock = max(0, item['laptop'].stock - item['quantity'])
                item['laptop'].save(update_fields=['stock'])
            cart.clear()
            return redirect('store:order_success', order_id=order.id)
    else:
        form = CheckoutForm(initial={'full_name': request.user.get_full_name() or request.user.username})

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
@require_POST
def wishlist_toggle(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, laptop=laptop)
    if not created:
        obj.delete()
        messages.info(request, f'Removed {laptop.name} from wishlist.')
    else:
        messages.success(request, f'Added {laptop.name} to wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'store:wishlist'))


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('laptop')
    return render(request, 'store/wishlist.html', {'items': items})


@require_POST
def compare_toggle(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id)
    compare_ids = request.session.get('compare', [])
    if laptop.id in compare_ids:
        compare_ids.remove(laptop.id)
    else:
        if len(compare_ids) >= 3:
            messages.warning(request, 'You can compare up to 3 laptops at a time.')
        else:
            compare_ids.append(laptop.id)
    request.session['compare'] = compare_ids
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'store:product_list'))


def compare_view(request):
    compare_ids = request.session.get('compare', [])
    laptops = list(Laptop.objects.filter(id__in=compare_ids))
    laptops.sort(key=lambda l: compare_ids.index(l.id))

    spec_rows = [
        ('Brand', lambda l: l.brand.name),
        ('Price', lambda l: f'${l.current_price}'),
        ('CPU', lambda l: l.cpu),
        ('CPU Cores', lambda l: l.cpu_cores),
        ('RAM', lambda l: f'{l.ram_gb} GB'),
        ('Storage', lambda l: f'{l.storage_gb} GB {l.storage_type}'),
        ('GPU', lambda l: l.gpu),
        ('Screen', lambda l: f'{l.screen_size}" {l.resolution}'),
        ('Refresh rate', lambda l: f'{l.refresh_rate} Hz'),
        ('Battery', lambda l: f'{l.battery_wh} Wh'),
        ('Weight', lambda l: f'{l.weight_kg} kg'),
        ('OS', lambda l: l.os),
        ('Rating', lambda l: f'{l.average_rating} / 5'),
    ]
    table = [(label, [fn(l) for l in laptops]) for label, fn in spec_rows]

    return render(request, 'store/compare.html', {'laptops': laptops, 'table': table})


def compare_clear(request):
    request.session['compare'] = []
    request.session.modified = True
    return redirect('store:compare')


staff_required = user_passes_test(lambda user: user.is_staff)


@staff_required
def dashboard(request):
    products = Laptop.objects.select_related('brand', 'category').all()
    return render(request, 'store/dashboard.html', {
        'products': products,
        'total_products': products.count(),
        'active_products': products.filter(is_active=True).count(),
        'low_stock_count': products.filter(stock__lte=3, stock__gt=0).count(),
        'out_of_stock_count': products.filter(stock=0).count(),
    })


@staff_required
def dashboard_product_form(request, laptop_id=None):
    laptop = get_object_or_404(Laptop, pk=laptop_id) if laptop_id else None
    form = LaptopAdminForm(request.POST or None, request.FILES or None, instance=laptop)
    if request.method == 'POST' and form.is_valid():
        product = form.save()
        messages.success(request, f'{product.name} has been {"updated" if laptop else "added"}.')
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_product_form.html', {
        'form': form,
        'laptop': laptop,
    })


@staff_required
@require_POST
def dashboard_product_delete(request, laptop_id):
    laptop = get_object_or_404(Laptop, pk=laptop_id)
    name = laptop.name
    laptop.delete()
    messages.success(request, f'{name} has been deleted.')
    return redirect('store:dashboard')
