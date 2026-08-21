import logging
import os
import resend
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _get_resend_config():
    """
    Obtiene la API Key y el remitente desde settings o variables de entorno.
    """
    api_key = getattr(settings, "RESEND_API_KEY", "") or os.getenv("RESEND_API_KEY", "").strip()
    from_email = getattr(settings, "RESEND_FROM_EMAIL", "") or os.getenv(
        "RESEND_FROM_EMAIL", "UNI Open Source <onboarding@resend.dev>"
    ).strip()
    return api_key, from_email


def _send_resend_email(to_email, subject, html_content, text_content):
    """
    Envía un correo electrónico a través de la API REST HTTPS de Resend.
    Retorna True si el correo fue aceptado por la API de Resend, False en caso contrario.
    """
    api_key, from_email = _get_resend_config()

    if not api_key:
        logger.error(
            "[RESEND EMAIL] Error: RESEND_API_KEY no está configurada en las variables de entorno."
        )
        return False

    resend.api_key = api_key

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
        "text": text_content,
    }

    try:
        response = resend.Emails.send(params)
        logger.info(f"[RESEND EMAIL SUCCESS] Correo enviado a {to_email} - ID: {response.get('id', 'N/A')}")
        return True
    except Exception as err:
        logger.error(f"[RESEND EMAIL ERROR] Falló el envío a {to_email}: {str(err)}")
        return False


def send_verification_email(to_email, code, action_type="register"):
    """
    Envía el correo de verificación con el código de 6 dígitos al usuario usando Resend.
    """
    if action_type == "resend":
        subject = "Nuevo Código de Verificación - UNI Open Source"
        text_body = (
            f"Hola,\n\nTu nuevo código de verificación es: {code}\n\n"
            f"Este código es válido por 15 minutos.\n\nBienvenido a UNI Open Source."
        )
    else:
        subject = "Código de Verificación - UNI Open Source"
        text_body = (
            f"Hola,\n\nTu código de verificación para UNI Open Source es: {code}\n\n"
            f"Este código es válido por 15 minutos.\n\nBienvenido a la plataforma."
        )

    try:
        html_body = render_to_string(
            "web/emails/verification_code.html",
            {
                "code": code,
                "action_type": action_type,
            },
        )
    except Exception as e:
        logger.warning(f"[EMAIL RENDER WARNING] Falló render_to_string HTML: {e}. Usando texto plano.")
        html_body = f"<p>{text_body.replace('\n', '<br>')}</p>"

    logger.info(f"[EMAIL SERVICE] Despachando correo de verificación a {to_email} ({action_type})")
    return _send_resend_email(to_email, subject, html_body, text_body)


def send_password_reset_email(to_email, link):
    """
    Envía el correo de restablecimiento de contraseña usando Resend.
    """
    subject = "Recupera tu contraseña - UNI Open Source"
    text_body = (
        f"Hola,\n\nHemos recibido una solicitud para cambiar tu contraseña en UNI Open Source.\n\n"
        f"Haz clic en el siguiente enlace para crear una nueva:\n{link}\n\n"
        f"Si no fuiste tú, simplemente ignora este mensaje."
    )

    try:
        html_body = render_to_string(
            "web/emails/password_reset.html",
            {
                "link": link,
            },
        )
    except Exception as e:
        logger.warning(f"[EMAIL RENDER WARNING] Falló render_to_string HTML: {e}. Usando texto plano.")
        html_body = f"<p>{text_body.replace('\n', '<br>')}</p>"

    logger.info(f"[EMAIL SERVICE] Despachando enlace de recuperación a {to_email}")
    return _send_resend_email(to_email, subject, html_body, text_body)
