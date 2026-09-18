from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:laptop_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:laptop_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:laptop_id>/', views.cart_remove, name='cart_remove'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('orders/', views.order_history, name='order_history'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:laptop_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    path('compare/', views.compare_view, name='compare'),
    path('compare/toggle/<int:laptop_id>/', views.compare_toggle, name='compare_toggle'),
    path('compare/clear/', views.compare_clear, name='compare_clear'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/new/', views.dashboard_product_form, name='dashboard_product_add'),
    path('dashboard/products/<int:laptop_id>/edit/', views.dashboard_product_form, name='dashboard_product_edit'),
    path('dashboard/products/<int:laptop_id>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),
]
