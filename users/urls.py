from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [

    path("", views.index_view, name="index"),

    path("login/", views.login_view, name="login"),

    path("register/", views.register_view, name="register"),

    path("perfil/", views.profile_view, name="profile"),

    path("logout/", auth_views.LogoutView.as_view(next_page="index"), name="logout"),

    # ==========================================
    # RECUPERAR CONTRASEÑA (FLUJO PERSONALIZADO)
    # ==========================================
    
    # Paso 1: Pantalla para pedir el correo (Incluye el modal de "Enviado")
    path(
        "reset_password/", 
        views.reset_password_request_view, 
        name="reset_password"
    ),

    # Paso 2: Pantalla para escribir la nueva clave (Incluye el modal de "Éxito")
    path(
        "reset/<uidb64>/<token>/", 
        views.reset_password_confirm_view, 
        name="password_reset_confirm"
    ),
]