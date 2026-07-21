from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Autenticación básica
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("perfil/", views.profile_view, name="profile"),
    path("logout/", auth_views.LogoutView.as_view(next_page="index"), name="logout"),
    
    # Recuperación de contraseña
    path("reset_password/", views.reset_password_request_view, name="reset_password"),
    path("reset/<uidb64>/<token>/", views.reset_password_confirm_view, name="password_reset_confirm"),
    
    # APIs internas (Llamadas desde JavaScript)
    path("api/check-username/", views.check_username_api, name="check_username_api"),
    path("api/verify-code/", views.verify_code_api, name="verify_code_api"),
    path("api/resend-code/", views.resend_code_api, name="resend_code_api"),
    path("api/update-profile/", views.update_profile_api, name="update_profile_api"), # NUEVA RUTA AÑADIDA
]