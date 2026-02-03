# from django.urls import path
# from . import views

# urlpatterns = [
#     path('signup/', views.signup, name='signup'),
#     path('login/', views.handleLogin, name='handleLogin'),
#     path('logout/', views.handleLogout, name='handleLogout'),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.handleLogin, name='handleLogin'),
    path('logout/', views.handleLogout, name='handleLogout'),
    path('signin/', views.handleLogin, name='signin'),
]
