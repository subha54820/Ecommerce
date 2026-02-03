# from django.shortcuts import render,redirect
# def signup(request):
#     return render(request,"authonatication/signup.html")

# def handleLogin(request):
#     return render(request,"authonatication/Login.html")

# def handleLogout(request):
#     return redirect('/authercart/Login')
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User

def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["pass1"]
        confirm_password = request.POST["pass2"]
        if password != confirm_password:
            return HttpResponse("Password Not Matching")
            # return render(request, 'auth/signup.html')
        try:
            if User.objects.get(username = email):
                return HttpResponse("emil already exists")
                # return render(request, 'auth/signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(email, email, password)
        user.save()
        return HttpResponse("User created", email)
        
    return render(request, "signup.html")

def handleLogin(request):
    return render(request, "Login.html")

def handleLogout(request):
    return redirect('/auth/login/')
