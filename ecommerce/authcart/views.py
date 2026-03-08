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
        username = request.POST.get("username", "")
        password = request.POST.get("pass1", "")
        confirm_password = request.POST.get("pass2", "")
        
        # Validation
        if not username or not password:
            messages.error(request, "Name and password are required")
            return render(request, "signup.html")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "signup.html")
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "signup.html")
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "This name is already taken")
            return render(request, "signup.html")
        
        # Create user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            
            messages.success(request, "Account created successfully! Please login.")
            return redirect('handleLogin')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "signup.html")

    return render(request, "signup.html")

def handleLogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("pass", "")
        
        if not username or not password:
            messages.error(request, "Name and password are required")
            return render(request, "Login.html")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid name or password")
            return render(request, "Login.html")
    
    return render(request, "Login.html")

def handleLogout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('index')
