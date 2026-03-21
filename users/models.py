from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Relación 1 a 1: Si se borra el User, se borra este Profile (CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Información general
    bio = models.TextField(max_length=200, blank=True, null=True, help_text="Descripción detallada sobre ti")
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True, null=True)
    
    # Enlaces y Contacto
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()