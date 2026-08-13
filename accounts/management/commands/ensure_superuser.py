import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crea automáticamente una cuenta de superusuario si no existe en la base de datos para el despliegue."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin').strip()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@uniopensource.com').strip()
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin12345').strip()

        if not username or not password:
            self.stdout.write(self.style.WARNING("Variables DJANGO_SUPERUSER_USERNAME o DJANGO_SUPERUSER_PASSWORD no configuradas."))
            return

        if not User.objects.filter(username__iexact=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"[SUPERUSER] Cuenta '{username}' creada exitosamente."))
        else:
            self.stdout.write(self.style.SUCCESS(f"[SUPERUSER] La cuenta '{username}' ya existe."))
