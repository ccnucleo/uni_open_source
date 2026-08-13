import json
import os
import urllib.request
import urllib.parse
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(to_email, code, action_type="register"):
    """
    Envía el correo con el código de verificación usando Google Apps Script (Web App via HTTP POST).
    Si GOOGLE_APPS_SCRIPT_URL no está configurado, utiliza el backend predeterminado de Django.
    """
    script_url = os.getenv("GOOGLE_APPS_SCRIPT_URL", "").strip()
    secret_key = os.getenv("GOOGLE_APPS_SCRIPT_SECRET", "").strip()

    if action_type == "resend":
        subject = "Nuevo Código de Verificación - UNI Open Source"
        body = f"Tu nuevo código de verificación es: {code}\n\nBienvenido a la plataforma."
    else:
        subject = "Código de Verificación - UNI Open Source"
        body = f"Tu código de verificación es: {code}\n\nBienvenido a la plataforma."

    # Imprimir siempre en logs para respaldo y depuración
    print(f"[EMAIL SERVICE] Código generado para {to_email} ({action_type}): {code}")

    if script_url:
        payload = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "code": code,
            "type": action_type,
            "secret": secret_key
        }
        return _send_via_apps_script(script_url, payload, subject, body, to_email)
    else:
        return _fallback_send_mail(subject, body, to_email)


def send_password_reset_email(to_email, link):
    """
    Envía el correo de recuperación de contraseña usando Google Apps Script o el backend predeterminado.
    """
    script_url = os.getenv("GOOGLE_APPS_SCRIPT_URL", "").strip()
    secret_key = os.getenv("GOOGLE_APPS_SCRIPT_SECRET", "").strip()

    subject = "Recupera tu contraseña - UNI Open Source"
    body = (
        f"Hola,\n\nHemos recibido una solicitud para cambiar tu contraseña.\n\n"
        f"Haz clic en el siguiente enlace para crear una nueva:\n{link}\n\n"
        f"Si no fuiste tú, simplemente ignora este mensaje."
    )

    print(f"[EMAIL SERVICE] Enlace de recuperación generado para {to_email}: {link}")

    if script_url:
        payload = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "link": link,
            "type": "password_reset",
            "secret": secret_key
        }
        return _send_via_apps_script(script_url, payload, subject, body, to_email)
    else:
        return _fallback_send_mail(subject, body, to_email)


def _send_via_apps_script(script_url, payload, subject, body, to_email):
    """
    Realiza una petición HTTP POST a la URL de Google Apps Script Web App.
    """
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            script_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            resp_text = response.read().decode("utf-8")
            print(f"[APPS SCRIPT SUCCESS] Correo enviado a {to_email} vía Google Apps Script: {resp_text}")
            return True
    except Exception as err:
        print(f"[APPS SCRIPT ERROR] Falló el envío vía Google Apps Script ({err}). Intentando fallback a Django...")
        return _fallback_send_mail(subject, body, to_email)


def _fallback_send_mail(subject, body, to_email):
    """
    Envío tradicional mediante la configuración de correo de Django.
    """
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or "noreply@uniopensource.com"
        send_mail(
            subject,
            body,
            from_email,
            [to_email],
            fail_silently=True,
        )
        print(f"[DJANGO MAIL SUCCESS] Correo enviado vía Django SMTP a {to_email}")
        return True
    except Exception as err:
        print(f"[DJANGO MAIL ERROR] Error al enviar vía Django: {err}")
        return False
