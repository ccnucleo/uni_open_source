from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    # Ruta principal: Lista de todos los desarrolladores
    path("", views.community_list_view, name="list"),
    
    # Ruta de detalle: El perfil público de un usuario específico
    path("<str:username>/", views.community_profile_view, name="profile"),
]