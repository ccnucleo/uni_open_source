from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import random
import json
from django.core.mail import send_mail
from django.http import JsonResponse
import os

# Imports necesarios para encriptar el enlace de recuperación
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

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
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        # Validación normal de errores
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect("register")

        # 1. Generar código de 6 dígitos
        codigo_verificacion = str(random.randint(100000, 999999))

        # 2. Guardar datos TEMPORALMENTE en la sesión (no creamos el usuario aún)
        request.session['temp_user_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'codigo': codigo_verificacion
        }

        # 3. Enviar el correo de verdad (Usando tu .env)
        try:
            send_mail(
                'Código de Verificación - UNI Open Source',
                f'Tu código de verificación es: {codigo_verificacion}\n\nBienvenido a la plataforma.',
                os.getenv('EMAIL_USER'),
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, "Hubo un error al enviar el correo. Intenta de nuevo.")
            return redirect("register")

        # 4. Recargar la página abriendo el Modal
        return render(request, "users/auth/register.html", {
            "show_modal": True, 
            "email_digitado": email
        })

    return render(request, "users/auth/register.html")

# ==========================================
# APIs PARA QUE JAVASCRIPT HABLE CON DJANGO
# ==========================================

def check_username_api(request):
    """API para que la ventanita sutil revise si el usuario existe en tiempo real"""
    username = request.GET.get('username', '').lower()
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'is_taken': is_taken})

def verify_code_api(request):
    """API para verificar los 6 dígitos del modal"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            codigo_ingresado = data.get('code')
            
            temp_data = request.session.get('temp_user_data')
            
            if not temp_data:
                return JsonResponse({'success': False, 'error': 'La sesión expiró. Vuelve a registrarte.'})

            # Si el código es correcto, CREAMOS AL USUARIO
            if codigo_ingresado == temp_data['codigo']:
                User.objects.create_user(
                    username=temp_data['username'],
                    email=temp_data['email'],
                    password=temp_data['password']
                )
                # Limpiamos la memoria temporal
                del request.session['temp_user_data']
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'El código es incorrecto.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Error de servidor.'})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

def resend_code_api(request):
    """API para reenviar el código de 6 dígitos"""
    if request.method == "POST":
        temp_data = request.session.get('temp_user_data')
        
        if not temp_data:
            return JsonResponse({'success': False, 'error': 'La sesión expiró.'})

        # 1. Generamos un código NUEVO
        nuevo_codigo = str(random.randint(100000, 999999))
        
        # 2. Lo actualizamos en la sesión temporal
        temp_data['codigo'] = nuevo_codigo
        request.session['temp_user_data'] = temp_data
        
        # 3. Enviamos el correo de nuevo (Usando tu .env)
        email = temp_data['email']
        try:
            send_mail(
                'Nuevo Código de Verificación - UNI Open Source',
                f'Tu nuevo código de verificación es: {nuevo_codigo}\n\nBienvenido a la plataforma.',
                os.getenv('EMAIL_USER'),
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Error al enviar correo.'})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# ==========================================
# RECUPERAR CONTRASEÑA (PASO 1: PEDIR CORREO)
# ==========================================
@never_cache
def reset_password_request_view(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        
        user = User.objects.filter(email=email).first()

        if user:
            # 1. Generamos un token de un solo uso
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # 2. Armamos el enlace
            dominio = request.get_host()
            link = f"http://{dominio}/reset/{uid}/{token}/"

            # 3. Enviamos el correo
            try:
                send_mail(
                    'Recupera tu contraseña - UNI Open Source',
                    f'Hola,\n\nHemos recibido una solicitud para cambiar tu contraseña.\n\nHaz clic en el siguiente enlace para crear una nueva:\n{link}\n\nSi no fuiste tú, simplemente ignora este mensaje.',
                    os.getenv('EMAIL_USER'),
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error al enviar correo: {e}")

        # 4. SEGURIDAD: Mostrar éxito siempre, exista o no
        return render(request, "users/auth/reset_password_request.html", {"show_modal": True})

    return render(request, "users/auth/reset_password_request.html")

# ==========================================
# RECUPERAR CONTRASEÑA (PASO 2: CAMBIAR CLAVE)
# ==========================================
@never_cache
def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')

            if user.check_password(new_password):
                messages.error(request, 'La nueva contraseña no puede ser igual a la actual.')
                return render(request, 'users/auth/reset_password_confirm.html')

            user.set_password(new_password)
            user.save()
            return render(request, 'users/auth/reset_password_confirm.html', {'show_success_modal': True})
            
        return render(request, 'users/auth/reset_password_confirm.html')
    
    else:
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('login')