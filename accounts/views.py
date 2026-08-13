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

# Servicio centralizado de envíos de correo (Google Apps Script / SMTP Fallback)
from core.emails import send_verification_email, send_password_reset_email

# Modelos locales de la app accounts
from .models import UnverifiedUser, Profile, Technology, Interest

# Modelos de la app projects y courses
from projects.models import Tag as ProjectTag, Technology as ProjectTechnology, Project
from courses.models import Tag as CourseTag
from django.conf import settings
from django.db.models import Count


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

    project_tags = set(ProjectTag.objects.values_list("name", flat=True))
    course_tags = set(CourseTag.objects.values_list("name", flat=True))
    project_techs = set(ProjectTechnology.objects.values_list("name", flat=True))
    unique_tags = {t.strip().lower() for t in (project_tags | course_tags | project_techs) if t and t.strip()}
    total_tecnologias = len(unique_tags)

    proyectos_destacados = (
        Project.objects.filter(is_public=True)
        .select_related("owner")
        .prefetch_related("technologies", "tags")
        .annotate(likes_count=Count("likes", distinct=True))
        .order_by("-likes_count", "-created_at")[:6]
    )

    return render(
        request,
        "web/pages/home/index.html",
        {
            "active_section": "home",
            "page_title": "Inicio",
            "colaboradores": colaboradores,
            "total_proyectos": total_proyectos,
            "total_usuarios": total_usuarios,
            "total_tecnologias": total_tecnologias,
            "proyectos_destacados": proyectos_destacados,
        },
    )

def quienes_somos_view(request):
    return render(
        request,
        "web/pages/static/quienes_somos.html",
        {
            "page_title": "¿Quiénes Somos?",
        },
    )


def terminos_view(request):
    return render(
        request,
        "web/pages/static/terminos.html",
        {
            "page_title": "Términos de Uso",
        },
    )


def privacidad_view(request):
    return render(
        request,
        "web/pages/static/privacidad.html",
        {
            "page_title": "Política de Privacidad",
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
    from projects.models import Project
    from django.db.models import Q
    
    # Extraemos TODOS los datos (en uso y pre-creados) para el autocompletado del modal
    all_tags = list(ProjectTag.objects.values_list('name', flat=True))
    all_techs = list(ProjectTechnology.objects.values_list('name', flat=True))
    all_users = list(User.objects.exclude(username=request.user.username).values_list('username', flat=True))
    
    my_projects = Project.objects.filter(Q(owner=request.user) | Q(collaborators=request.user)).distinct().order_by('-created_at')

    return render(
        request,
        "web/pages/profile/profile.html",
        {
            "active_section": "profile",
            "page_title": "Mi perfil",
            # Enviamos las listas convertidas a JSON para que JavaScript pueda leerlas sin problemas
            "all_tags": json.dumps(all_tags),
            "all_techs": json.dumps(all_techs),
            "all_users": json.dumps(all_users),
            "my_projects": my_projects,
        },
    )


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        raw_email = request.POST.get("email") or ""
        email = raw_email.lower().strip()
        password = request.POST.get("password") or ""
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()

        if not username or not email or not password:
            messages.error(request, "Por favor completa todos los campos obligatorios.")
            return redirect("accounts:register")

        if first_name and (len(first_name) < 2 or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', first_name)):
            messages.error(request, "El nombre debe ser válido y sin caracteres especiales ni números.")
            return redirect("accounts:register")
            
        if last_name and (len(last_name) < 2 or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name)):
            messages.error(request, "El apellido debe ser válido y sin caracteres especiales ni números.")
            return redirect("accounts:register")

        try:
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "El usuario ya existe.")
                return redirect("accounts:register")

            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, "El correo ya está registrado.")
                return redirect("accounts:register")

            codigo_verificacion = str(random.randint(100000, 999999))
            
            UnverifiedUser.objects.filter(email__iexact=email).delete()
            UnverifiedUser.objects.create(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                verification_code=codigo_verificacion
            )
        except Exception as err:
            messages.error(request, f"Error al guardar datos de registro: {str(err)}")
            return redirect("accounts:register")

        send_verification_email(email, codigo_verificacion, action_type="register")

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
    username = request.GET.get("username", "").strip()
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"is_taken": is_taken})


def verify_code_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8")) if request.body else {}
            codigo_ingresado = str(data.get("code", "")).strip()
            email_ingresado = str(data.get("email", "")).strip().lower()

            if not email_ingresado or not codigo_ingresado:
                return JsonResponse({"success": False, "error": "Datos incompletos."})

            temp_user = UnverifiedUser.objects.filter(email__iexact=email_ingresado).first()

            if not temp_user:
                return JsonResponse({"success": False, "error": "No hay un registro pendiente. Vuelve a registrarte."})

            if temp_user.is_code_expired():
                temp_user.delete()
                return JsonResponse({"success": False, "error": "El código ha expirado. Vuelve a registrarte."})

            if codigo_ingresado == temp_user.verification_code:
                if User.objects.filter(username__iexact=temp_user.username).exists():
                    return JsonResponse({"success": False, "error": "El usuario ya fue registrado."})

                if User.objects.filter(email__iexact=temp_user.email).exists():
                    return JsonResponse({"success": False, "error": "El correo ya fue registrado."})

                new_user = User(
                    username=temp_user.username,
                    email=temp_user.email,
                    password=temp_user.password, # Contraseña ya cifrada en UnverifiedUser.save()
                    first_name=temp_user.first_name,
                    last_name=temp_user.last_name,
                    is_active=True
                )
                new_user.save()
                temp_user.delete()
                
                # Iniciar sesión automáticamente
                login(request, new_user)
                return JsonResponse({"success": True})

            return JsonResponse({"success": False, "error": "El código es incorrecto."})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error de servidor: {str(e)}"})

    return JsonResponse({"success": False, "error": "Método no permitido."})


def resend_code_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8")) if request.body else {}
            email_ingresado = str(data.get("email", "")).strip().lower()
            
            temp_user = UnverifiedUser.objects.filter(email__iexact=email_ingresado).first()

            if not temp_user:
                return JsonResponse({"success": False, "error": "No hay registro pendiente."})

            nuevo_codigo = str(random.randint(100000, 999999))
            temp_user.verification_code = nuevo_codigo
            temp_user.created_at = timezone.now()
            temp_user.save()

            send_verification_email(temp_user.email, nuevo_codigo, action_type="resend")
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error al procesar reenvío: {str(e)}"})

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

            send_password_reset_email(email, link)

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
                    if contact_email: 
                        validate_email(contact_email)
                        profile.contact_email = contact_email
                    else:
                        profile.contact_email = None
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