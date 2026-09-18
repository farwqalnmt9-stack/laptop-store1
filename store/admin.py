from django.contrib import admin
from .models import Brand, Category, Laptop, Review, Wishlist, Order, OrderItem


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'discount_price', 'stock', 'is_featured', 'is_active']
    list_filter = ['brand', 'category', 'storage_type', 'is_featured', 'is_active']
    search_fields = ['name', 'cpu', 'gpu', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_featured', 'is_active']
    fieldsets = (
        ('Identity', {'fields': ('name', 'slug', 'brand', 'category', 'sku', 'description')}),
        ('Performance', {'fields': ('cpu', 'cpu_cores', 'ram_gb', 'gpu', 'storage_gb', 'storage_type')}),
        ('Display & Build', {'fields': ('screen_size', 'resolution', 'refresh_rate', 'weight_kg', 'battery_wh', 'os')}),
        ('Commerce', {'fields': ('price', 'discount_price', 'stock', 'is_featured', 'is_active')}),
        ('Images', {'fields': ('image', 'image_2', 'image_3')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['laptop', 'user', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'laptop', 'added_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['laptop_name', 'unit_price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'city', 'status', 'total', 'created_at']
    list_filter = ['status', 'city']
    list_editable = ['status']
    inlines = [OrderItemInline]
    search_fields = ['full_name', 'phone', 'user__username']
