from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile, Wishlist
from django.db.models import Sum

def base(request):
    return render(request, "base.html")

def contact(request):
    return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def home(request):
    query = request.GET.get('search')
    filter_val = request.GET.get('filter')
    
    if query:
        products = Product.objects.filter(name__icontains=query)
    elif filter_val and filter_val != 'all':
        # Handled by Isotope in frontend, but good to filter backend too if needed
        # Actually standard Isotope setup here uses data-filter, so view normally sends all.
        # But per user request, we only want "Product" category on main home.
        products = Product.objects.all()
    else:
        # Default homepage view: only show "Product" category
        products = Product.objects.filter(category__name='Product')
        if not products.exists():
            # Fallback if category is empty
            products = Product.objects.all()
            
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'search_query': query,
        'wishlist_ids': list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)) if request.user.is_authenticated else []
    }
    return render(request, "index.html", context)

def index(request):
    return home(request)

# Profile View
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

def profile(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            # Direct Profile Creation (Signup) Logic
            email = request.POST.get("email", "")
            password = request.POST.get("pass1", "")
            confirm_password = request.POST.get("pass2", "")
            
            if not email or not password:
                messages.error(request, "Email and password are required")
                return render(request, "profile.html", {'profile': None, 'orders': []})
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return render(request, "profile.html", {'profile': None, 'orders': []})
            
            if len(password) < 6:
                messages.error(request, "Password must be at least 6 characters")
                return render(request, "profile.html", {'profile': None, 'orders': []})
            
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already exists")
                return render(request, "profile.html", {'profile': None, 'orders': []})
            
            try:
                user = User.objects.create_user(username=email, email=email, password=password)
                user.save()
                login(request, user)
                messages.success(request, f"Welcome {email}! Your profile has been created.")
                return redirect('profile')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return render(request, "profile.html", {'profile': None, 'orders': []})
        
        return render(request, "profile.html", {'profile': None, 'orders': []})
        
    # Get or create user profile for authenticated user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle profile update for authenticated user
    if request.method == "POST":
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.zipcode = request.POST.get('zipcode', '')
        profile.country = request.POST.get('country', 'India')
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    # Get user orders
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, "profile.html", context)

# Cart View
def cart_view(request):
    if not request.user.is_authenticated:
        messages.info(request, "Your cart is synchronized across devices when you login.")
        # For now, we can handle session-based cart or just show empty for guest
        # Based on previous implementation, let's assume we want them to login to see their saved cart
        # or we just show an message.
        return render(request, "cart.html", {'cart': None, 'cart_items': []})


# Wishlist Views
def wishlist_view(request):
    """Display current user wishlist items."""
    if request.user.is_authenticated:
        wish_items = Wishlist.objects.filter(user=request.user)
    else:
        wish_items = []
    context = {'wish_items': wish_items}
    return render(request, 'wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    action = "added"
    if created:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        obj.delete()
        action = "removed"
        messages.info(request, f"{product.name} removed from your wishlist.")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
            'message': f"{product.name} {'added to' if action == 'added' else 'removed from'} your wishlist."
        })
        
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def remove_from_wishlist(request, product_id):
    item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()
    if item:
        item.delete()
        messages.success(request, "Item removed from wishlist.")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
            'message': 'Item removed from wishlist.'
        })
    return redirect('wishlist')


# Cart View
def cart_view(request):
    if not request.user.is_authenticated:
        messages.info(request, "Your cart is synchronized across devices when you login.")
        return render(request, "cart.html", {'cart': None, 'cart_items': []})

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, "cart.html", context)

def get_cart_items(request):
    if not request.user.is_authenticated:
        return JsonResponse({'items': [], 'total_price': 0})
    
    try:
        cart = Cart.objects.get(user=request.user)
        items = []
        for item in cart.items.all():
            items.append({
                'name': item.product.name,
                'quantity': item.quantity,
                'price': float(item.product.price),
                'subtotal': float(item.subtotal),
                'image': item.product.image.url if item.product.image else ''
            })
        return JsonResponse({
            'items': items,
            'total_price': float(cart.total_price),
            'cart_count': cart.total_items
        })
    except Cart.DoesNotExist:
        return JsonResponse({'items': [], 'total_price': 0, 'cart_count': 0})

# Add to Cart
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to add items to your cart.")
        return redirect('handleLogin')

    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock!")
        return redirect('index')
    
    # Check if a specific quantity was requested
    requested_qty = int(request.GET.get('qty', 1))
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product already in cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        # Update quantity
        new_qty = cart_item.quantity + requested_qty
        if new_qty <= product.stock:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, f"Updated {product.name} quantity to {cart_item.quantity}")
        else:
            cart_item.quantity = product.stock # Max out at stock
            cart_item.save()
            messages.warning(request, f"Only {product.stock} items available. Added maximum possible.")
    else:
        # Set requested quantity for new item
        if requested_qty <= product.stock:
            cart_item.quantity = requested_qty
            cart_item.save()
            messages.success(request, f"Added {requested_qty} x {product.name} to cart!")
        else:
            cart_item.quantity = product.stock
            cart_item.save()
            messages.warning(request, f"Only {product.stock} items available. Added maximum possible.")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.total_items,
            'message': f"Added {product.name} to cart!"
        })
    return redirect('cart')

# Remove from Cart
def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('handleLogin')
        
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"Removed {product_name} from cart")
    return redirect('cart')

# Update Cart Item Quantity
def update_cart(request, item_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Please login'})
        return redirect('handleLogin')

    if request.method == "POST" or (request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest'):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if request.method == "POST":
            quantity = int(request.POST.get('quantity', 1))
        else: # AJAX GET request for +/- buttons
            action = request.GET.get('action')
            if action == 'plus':
                quantity = cart_item.quantity + 1
            elif action == 'minus':
                quantity = cart_item.quantity - 1
            else:
                quantity = cart_item.quantity

        if quantity <= 0:
            cart_item.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'action': 'removed',
                    'cart_count': Cart.objects.get(user=request.user).total_items,
                    'total_price': float(Cart.objects.get(user=request.user).total_price)
                })
            messages.success(request, "Item removed from cart")
        elif quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'quantity': cart_item.quantity,
                    'subtotal': float(cart_item.subtotal),
                    'cart_count': cart_item.cart.total_items,
                    'total_price': float(cart_item.cart.total_price)
                })
            messages.success(request, "Cart updated")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': f'Only {cart_item.product.stock} items available'})
            messages.error(request, f"Only {cart_item.product.stock} items available")
    
    return redirect('cart')

# Checkout View
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to proceed with checkout.")
        return redirect('handleLogin')

    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.warning(request, "Your cart is empty!")
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')
    
    # Get user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle order placement
    if request.method == "POST":
        # Get shipping details
        shipping_address = request.POST.get('address', '')
        shipping_city = request.POST.get('city', '')
        shipping_state = request.POST.get('state', '')
        shipping_zipcode = request.POST.get('zipcode', '')
        shipping_phone = request.POST.get('phone', '')
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Validate
        if not all([shipping_address, shipping_city, shipping_state, shipping_zipcode, shipping_phone]):
            messages.error(request, "Please fill all shipping details")
            return render(request, "checkout.html", {'cart': cart, 'profile': profile})
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            payment_method=payment_method,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_zipcode=shipping_zipcode,
            shipping_phone=shipping_phone,
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        # Send notification to owner
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"New Order Placed: {order.order_number}"
        message = f"""
        New order received!
        
        Order Number: {order.order_number}
        Customer: {request.user.username}
        Total Amount: ₹{order.total_amount}
        Payment Method: {order.get_payment_method_display()}
        
        Shipping Details:
        {order.shipping_address}
        {order.shipping_city}, {order.shipping_state} - {order.shipping_zipcode}
        Phone: {order.shipping_phone}
        
        Login to admin panel to view details.
        """
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [settings.OWNER_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
        
        messages.success(request, f"Order placed successfully! Order Number: {order.order_number}")
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'profile': profile,
    }
    return render(request, "checkout.html", context)

# Order Detail
def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('handleLogin')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, "order_detail.html", context)

# Order History
def order_history(request):
    if not request.user.is_authenticated:
        return redirect('handleLogin')

    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, "order_history.html", context)

from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile, Review

# Product Detail View
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get related products (same category, excluding current)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Handle Review Submission
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to leave a review")
            return redirect('handleLogin')
            
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully!")
            return redirect('product_detail', product_id=product.id)
    
    # Get reviews
    reviews = product.reviews.all()
    
    in_cart = False
    in_wishlist = False
    wishlist_ids = []
    if request.user.is_authenticated:
        cart_exists = CartItem.objects.filter(cart__user=request.user, product=product).exists()
        if cart_exists:
            in_cart = True

        # gather wishlist ids for this user to render add/remove buttons
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        if product.id in wishlist_ids:
            in_wishlist = True
            
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'wishlist_ids': wishlist_ids,
    }
    return render(request, "product_detail.html", context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    products = Product.objects.filter(name__icontains=query)[:5]
    suggestions = []
    for product in products:
        suggestions.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url if product.image else '',
            'url': f"/product/{product.id}/"
        })
    
    return JsonResponse({'suggestions': suggestions})
