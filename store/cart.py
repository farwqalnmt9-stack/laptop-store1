from decimal import Decimal
from .models import Laptop

CART_SESSION_KEY = 'cart'


class Cart:
    """Session-backed cart: {laptop_id(str): quantity(int)}"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, laptop, quantity=1, replace=False):
        laptop_id = str(laptop.id)
        if laptop_id not in self.cart:
            self.cart[laptop_id] = 0
        if replace:
            self.cart[laptop_id] = quantity
        else:
            self.cart[laptop_id] += quantity
        self.cart[laptop_id] = max(1, min(self.cart[laptop_id], laptop.stock or 1))
        self.save()

    def remove(self, laptop):
        laptop_id = str(laptop.id)
        if laptop_id in self.cart:
            del self.cart[laptop_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        laptop_ids = self.cart.keys()
        laptops = Laptop.objects.filter(id__in=laptop_ids)
        laptops_map = {str(l.id): l for l in laptops}
        for laptop_id, quantity in self.cart.items():
            laptop = laptops_map.get(laptop_id)
            if not laptop:
                continue
            yield {
                'laptop': laptop,
                'quantity': quantity,
                'unit_price': laptop.current_price,
                'subtotal': laptop.current_price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    @property
    def total(self):
        return sum(Decimal(item['subtotal']) for item in self)
