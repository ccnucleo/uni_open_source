from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [

    path("", views.index_view, name="index"),

    path("login/", views.login_view, name="login"),

    path("register/", views.register_view, name="register"),

    path("perfil/", views.profile_view, name="profile"),

    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html"
        ),
        name="reset_password",
    ),

    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]