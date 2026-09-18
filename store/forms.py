from django import forms
from .models import Review, Order, Laptop


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} stars') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={'placeholder': 'Sum up your experience'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us more...'}),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'city', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class LaptopAdminForm(forms.ModelForm):
    """Staff-only product editor; keeps validation beside the fields it governs."""

    class Meta:
        model = Laptop
        fields = [
            'name', 'brand', 'category', 'cpu', 'cpu_cores', 'ram_gb',
            'storage_gb', 'storage_type', 'gpu', 'screen_size', 'resolution',
            'refresh_rate', 'battery_wh', 'weight_kg', 'os', 'price',
            'discount_price', 'stock', 'sku', 'description', 'image', 'image_2',
            'image_3', 'is_featured', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'discount_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'screen_size': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'weight_kg': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }
