from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    # Ruta principal: Lista de todos los desarrolladores
    path("", views.community_list_view, name="list"),
    
    # API endpoints para interactuar con la comunidad
    path("api/follow/<int:user_id>/", views.toggle_follow_api, name="api_follow"),
    path("api/message/<int:user_id>/", views.send_message_api, name="api_message"),

    # Ruta de detalle: El perfil público de un usuario específico
    path("<str:username>/", views.community_profile_view, name="profile"),
]