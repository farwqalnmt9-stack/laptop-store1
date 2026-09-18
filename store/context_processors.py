from .cart import Cart


def cart_summary(request):
    cart = Cart(request)
    compare_ids = request.session.get('compare', [])
    return {
        'cart_count': len(cart),
        'compare_count': len(compare_ids),
    }
