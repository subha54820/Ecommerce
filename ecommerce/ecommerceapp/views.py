"""Module providing a function printing python version."""
from django.shortcuts import render

def base(request):
    return render(request, "base.html")

def contact(request):
    return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def home(request):
    return render(request, "index.html")

def index(request):
    return render(request, "index.html")
