"""Module providing a function printing python version."""
from django .urls import path
from ecommerceapp import views

urlpatterns = [
    path('',views.home,name="index"),
    path('contact',views.contact, name="contact"),
    path('about/',views.about, name="about"),
]
