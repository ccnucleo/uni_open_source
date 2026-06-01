import json
import os
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.utils import timezone

from .models import UnverifiedUser


@never_cache
def index_view(request):
    return render(
        request,
        "web/pages/home/index.html",
        {
            "active_section": "home",
            "page_title": "Inicio",
        },
    )


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

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
            return redirect("accounts:profile")
        messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "web/pages/auth/login.html")


@login_required(login_url="accounts:login")
@never_cache
def profile_view(request):
    return render(
        request,
        "web/pages/profile/profile.html",
        {
            "active_section": "profile",
            "page_title": "Mi perfil",
        },
    )


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("accounts:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect("accounts:register")

        codigo_verificacion = str(random.randint(100000, 999999))
        
        UnverifiedUser.objects.filter(email=email).delete()
        UnverifiedUser.objects.create(
            username=username,
            email=email,
            password=password, 
            verification_code=codigo_verificacion
        )

        try:
            send_mail(
                "Código de Verificación - UNI Open Source",
                f"Tu código de verificación es: {codigo_verificacion}\n\nBienvenido a la plataforma.",
                os.getenv("EMAIL_USER"),
                [email],
                fail_silently=False,
            )
        except Exception:
            messages.error(request, "Hubo un error al enviar el correo. Intenta de nuevo.")
            return redirect("accounts:register")

        return render(
            request,
            "web/pages/auth/register.html",
            {
                "show_modal": True,
                "email_digitado": email,
                "username_digitado": username, # Guardamos el nombre para que no se borre
            },
        )

    return render(request, "web/pages/auth/register.html")


def check_username_api(request):
    username = request.GET.get("username", "").lower()
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"is_taken": is_taken})


def verify_code_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            codigo_ingresado = data.get("code")
            email_ingresado = data.get("email")

            if not email_ingresado:
                return JsonResponse({"success": False, "error": "Falta el correo electrónico."})

            temp_user = UnverifiedUser.objects.filter(email=email_ingresado).first()

            if not temp_user:
                return JsonResponse({"success": False, "error": "No hay un registro pendiente. Vuelve a registrarte."})

            if temp_user.is_code_expired():
                temp_user.delete()
                return JsonResponse({"success": False, "error": "El código ha expirado. Vuelve a registrarte."})

            if codigo_ingresado == temp_user.verification_code:
                new_user = User(
                    username=temp_user.username,
                    email=temp_user.email,
                    password=temp_user.password 
                )
                new_user.save()
                
                temp_user.delete()
                return JsonResponse({"success": True})

            return JsonResponse({"success": False, "error": "El código es incorrecto."})
        except Exception:
            return JsonResponse({"success": False, "error": "Error de servidor."})

    return JsonResponse({"success": False, "error": "Método no permitido."})


def resend_code_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email_ingresado = data.get("email")
            
            temp_user = UnverifiedUser.objects.filter(email=email_ingresado).first()

            if not temp_user:
                return JsonResponse({"success": False, "error": "No hay registro pendiente."})

            nuevo_codigo = str(random.randint(100000, 999999))
            
            temp_user.verification_code = nuevo_codigo
            temp_user.created_at = timezone.now()
            temp_user.save()

            send_mail(
                "Nuevo Código de Verificación - UNI Open Source",
                f"Tu nuevo código de verificación es: {nuevo_codigo}\n\nBienvenido a la plataforma.",
                os.getenv("EMAIL_USER"),
                [temp_user.email],
                fail_silently=False,
            )
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False, "error": "Error al enviar correo."})

    return JsonResponse({"success": False, "error": "Método no permitido."})


@never_cache
def reset_password_request_view(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            dominio = request.get_host()
            link = f"http://{dominio}/reset/{uid}/{token}/"

            try:
                send_mail(
                    "Recupera tu contraseña - UNI Open Source",
                    f"Hola,\n\nHemos recibido una solicitud para cambiar tu contraseña.\n\nHaz clic en el siguiente enlace para crear una nueva:\n{link}\n\nSi no fuiste tú, simplemente ignora este mensaje.",
                    os.getenv("EMAIL_USER"),
                    [email],
                    fail_silently=False,
                )
            except Exception:
                pass

        return render(request, "web/pages/auth/reset_password_request.html", {"show_modal": True})

    return render(request, "web/pages/auth/reset_password_request.html")


@never_cache
def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")

            if user.check_password(new_password):
                messages.error(request, "La nueva contraseña no puede ser igual a la actual.")
                return render(request, "web/pages/auth/reset_password_confirm.html")

            user.set_password(new_password)
            user.save()
            return render(request, "web/pages/auth/reset_password_confirm.html", {"show_success_modal": True})

        return render(request, "web/pages/auth/reset_password_confirm.html")

    messages.error(request, "El enlace de recuperación es inválido o ha expirado.")
    return redirect("accounts:login")