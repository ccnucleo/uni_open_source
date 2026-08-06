import json
import os
import random
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.core.validators import URLValidator, validate_email
from django.core.exceptions import ValidationError

from .models import UnverifiedUser, Profile, Technology, Interest


from projects.models import Project
from django.conf import settings


@never_cache
def index_view(request):
    colaborators_dir = os.path.join(settings.BASE_DIR, "web", "static", "web", "img", "colaborators")
    colaboradores = []
    if os.path.exists(colaborators_dir):
        valid_exts = ('.png', '.jpg', '.jpeg', '.svg', '.webp')
        colaboradores = sorted([
            f for f in os.listdir(colaborators_dir)
            if f.lower().endswith(valid_exts)
        ])

    total_proyectos = Project.objects.count()
    total_usuarios = User.objects.count()

    return render(
        request,
        "web/pages/home/index.html",
        {
            "active_section": "home",
            "page_title": "Inicio",
            "colaboradores": colaboradores,
            "total_proyectos": total_proyectos,
            "total_usuarios": total_usuarios,
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
                "username_digitado": username,
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
            
            # EL ERROR ESTABA AQUÍ: Se agregó /accounts/ a la ruta
            link = f"http://{dominio}/accounts/reset/{uid}/{token}/"

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


def format_url(url):
    if url and not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

@login_required
def update_profile_api(request):
    if request.method == 'POST':
        try:
            user = request.user
            profile, _ = Profile.objects.get_or_create(user=user)
            update_type = request.POST.get('update_type')
            
            if update_type == 'basic_info':
                fname = request.POST.get('first_name', user.first_name)
                user.first_name = fname.strip() if fname else ""
                
                lname = request.POST.get('last_name', user.last_name)
                user.last_name = lname.strip() if lname else ""
                
                new_username = request.POST.get('username', '').strip()
                if new_username and new_username != user.username:
                    if User.objects.filter(username__iexact=new_username).exists():
                        return JsonResponse({'success': False, 'error': 'El nombre de usuario ya está ocupado.'})
                    user.username = new_username
                
                if 'avatar' in request.FILES:
                    profile.avatar = request.FILES['avatar']
                elif request.POST.get('remove_avatar') == 'true':
                    if profile.avatar:
                        profile.avatar.delete(save=False)
                    profile.avatar = None
                    
                user.save()
                profile.save()
                return JsonResponse({'success': True, 'message': 'Información básica actualizada correctamente.'})
                
            elif update_type == 'detailed_info':
                bio_val = request.POST.get('bio', profile.bio)
                if bio_val:
                    bio_val = bio_val.strip()
                    # REGEX: Limita los abusos de Enter a máximo 2 saltos consecutivos
                    bio_val = re.sub(r'\n{3,}', '\n\n', bio_val)
                profile.bio = bio_val if bio_val else ""
                
                val_url = URLValidator()
                
                linkedin_val = request.POST.get('linkedin', '').strip()
                linkedin = format_url(linkedin_val) if linkedin_val else ""
                
                github_val = request.POST.get('github', '').strip()
                github = format_url(github_val) if github_val else ""
                
                contact_email = request.POST.get('contact_email', '').strip()
                
                try:
                    if linkedin: val_url(linkedin)
                    profile.linkedin = linkedin
                except ValidationError:
                    return JsonResponse({'success': False, 'error': 'La URL de LinkedIn no es válida.'})
                    
                try:
                    if github: val_url(github)
                    profile.github = github
                except ValidationError:
                    return JsonResponse({'success': False, 'error': 'La URL de GitHub no es válida.'})
                    
                try:
                    if contact_email: validate_email(contact_email)
                    profile.contact_email = contact_email
                except ValidationError:
                    return JsonResponse({'success': False, 'error': 'El correo de contacto no es válido.'})
                
                tech_str = request.POST.get('tecnologias', '')
                profile.tecnologias.clear()
                if tech_str:
                    for name in [t.strip() for t in tech_str.split(',') if t.strip()]:
                        obj, _ = Technology.objects.get_or_create(nombre=name)
                        profile.tecnologias.add(obj)
                        
                int_str = request.POST.get('intereses', '')
                profile.intereses.clear()
                if int_str:
                    for name in [i.strip() for i in int_str.split(',') if i.strip()]:
                        obj, _ = Interest.objects.get_or_create(nombre=name)
                        profile.intereses.add(obj)
                        
                profile.save()
                return JsonResponse({'success': True, 'message': 'Perfil actualizado con éxito.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error del servidor: {str(e)}'})
            
    return JsonResponse({'success': False, 'error': 'Método no admitido.'})


@login_required(login_url="accounts:login")
@never_cache
def ajustes_view(request):
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "change_password":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Tu contraseña ha sido actualizada con éxito.")
                return redirect("ajustes")
            else:
                messages.error(request, "Por favor corrige los errores en el formulario de contraseña.")
        elif action == "delete_account":
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, "Tu cuenta y portafolio asociado han sido eliminados de forma permanente.")
            return redirect("index")

    return render(
        request,
        "web/pages/profile/ajustes.html",
        {
            "active_section": "settings",
            "page_title": "Ajustes",
            "password_form": password_form,
        },
    )