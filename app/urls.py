from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.user_dashboard, name='user_dashboard'),
    path('logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
]