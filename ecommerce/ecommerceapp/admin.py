from django.contrib import admin
from .models import Category, Product, UserProfile, Cart, CartItem, Order, OrderItem, ProductImage, Review

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'featured', 'created_at']
    list_filter = ['category', 'featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['featured', 'stock', 'price']
    inlines = [ProductImageInline]

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'phone']

# CartItem Inline
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal']

# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    inlines = [CartItemInline]
    readonly_fields = ['total_items', 'total_price']

# OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

# Order Admin
admin.site.register(Review)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
