from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.profile_view, name='profile'),
]