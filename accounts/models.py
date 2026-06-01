from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=200, blank=True, null=True, help_text="Descripción detallada sobre ti")
    avatar = models.ImageField(default="default.jpg", upload_to="profile_pics", blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = "users_profile"

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()

# =========================================================
# NUEVO MODELO: Usuario no verificado (Registro temporal)
# =========================================================
class UnverifiedUser(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) # Guardaremos el hash, no texto plano
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Encriptar la contraseña antes de guardarla si no está encriptada
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def is_code_expired(self):
        # El código expira después de 15 minutos (Checklist item 4)
        expiration_time = self.created_at + timedelta(minutes=15)
        return timezone.now() > expiration_time

    def __str__(self):
        return f"Pendiente: {self.email} - Expira: {self.created_at + timedelta(minutes=15)}"