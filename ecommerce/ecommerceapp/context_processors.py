from .models import Category, Cart

def all_categories(request):
    return {
        'all_categories': Category.objects.all()
    }

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {'cart_count': cart.total_items}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}
