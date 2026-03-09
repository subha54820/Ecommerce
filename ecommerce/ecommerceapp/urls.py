"""Module providing a function printing python version."""
from django .urls import path
from ecommerceapp import views

urlpatterns = [
    path('',views.home,name="index"),
    path('home',views.home,name="home"),
    path('contact',views.contact, name="contact"),
    path('about/',views.about, name="about"),
    
    # Profile
    path('profile/', views.profile, name="profile"),
    
    # Cart
    path('cart/', views.cart_view, name="cart"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name="remove_from_cart"),
    path('update-cart/<int:item_id>/', views.update_cart, name="update_cart"),
    path('get-cart-items/', views.get_cart_items, name="get_cart_items"),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name="checkout"),
    path('order/<int:order_id>/', views.order_detail, name="order_detail"),
    path('orders/', views.order_history, name="order_history"),
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),
    path('search-suggestions/', views.search_suggestions, name="search_suggestions"),
]
