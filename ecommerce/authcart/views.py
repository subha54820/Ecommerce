from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from ecommerceapp.models import UserProfile

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":
        email = request.POST.get("email", "")
        username = request.POST.get("username", "")
        password = request.POST.get("pass1", "")
        confirm_password = request.POST.get("pass2", "")
        
        # Validation
        if not username or not password:
            messages.error(request, "Name and password are required")
            return render(request, "signup.html")
        
        # Check if email exists (only if provided)
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered")
            return render(request, "signup.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "signup.html")
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "signup.html")
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "This name is already taken")
            return render(request, "signup.html")
        
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            messages.success(request, "Account created successfully! Please login.")
            next_url = request.POST.get('next')
            if next_url:
                # Forward to login page with the next parameter intact
                from urllib.parse import urlencode
                return redirect(f"/auth/login/?{urlencode({'next': next_url})}")
            return redirect('handleLogin')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "signup.html")

    return render(request, "signup.html")

def handleLogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":
        email_or_username = request.POST.get("username", "") # This comes from the 'email' input in the form
        password = request.POST.get("pass", "")
        
        if not email_or_username or not password:
            messages.error(request, "Security credentials are required")
            return render(request, "Login.html")
        
        # Try to find user by email first
        user_obj = User.objects.filter(email=email_or_username).first()
        if user_obj:
            username = user_obj.username
        else:
            # Fallback to username if email not found
            username = email_or_username

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials. Please check your email and password.")
            return render(request, "Login.html")
    
    return render(request, "Login.html")

def handleLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')
