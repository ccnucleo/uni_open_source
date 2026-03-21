from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@never_cache
def index_view(request):
    """Página de inicio - primer punto de acceso"""
    return render(request, "users/index.html")

@never_cache
def login_view(request):
    # SEGURIDAD: Si el usuario ya inició sesión, no tiene sentido que vea el login.
    # Lo redirigimos automáticamente a su perfil.
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "users/auth/login.html")


# SEGURIDAD: Este decorador obliga a iniciar sesión antes de ver el perfil.
# Si alguien no logueado intenta entrar, lo manda a la vista 'login'.
@login_required(login_url="login")
@never_cache
def profile_view(request):
    return render(request, "users/profile.html")

@never_cache
def register_view(request):
    # SEGURIDAD: Igual que en el login, si ya estás logueado, vas directo al perfil.
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Cuenta creada correctamente")
        return redirect("login")

    return render(request, "users/auth/register.html")