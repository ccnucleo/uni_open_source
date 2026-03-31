from django.conf import settings
from django.db import models


class Course(models.Model):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    LEVEL_CHOICES = [
        ("beginner", "Principiante"),
        ("intermediate", "Intermedio"),
        ("advanced", "Avanzado"),
        ("beg_int", "Principiante a Intermedio"),
        ("int_adv", "Intermedio a Avanzado"),
        ("all", "Todos los niveles"),
    ]

    # Nuevas opciones para saber de qué tipo de recurso se trata
    YOUTUBE = "youtube"
    PLATFORM = "platform"
    DOCS = "docs"
    RESOURCE_CHOICES = [
        (YOUTUBE, "Lista de YouTube"),
        (PLATFORM, "Plataforma Web (Coursera, Udemy, etc)"),
        (DOCS, "Documentación / Lectura"),
    ]

    title = models.CharField(max_length=120, verbose_name="Título del Curso")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="Descripción Corta")
    description = models.TextField(blank=True, verbose_name="Descripción Detallada")
    
    # Podrías crear un modelo Category separado después, pero por ahora lo dejamos como texto 
    # para que sea más fácil empezar (Ej: "Python", "Bases de Datos", "Git")
    category = models.CharField(max_length=80, blank=True, verbose_name="Categoría Temática")
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER, verbose_name="Nivel")
    
    
    url = models.URLField(max_length=500, blank=True, verbose_name="Enlace al curso gratuito")
    image = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True, verbose_name="Imagen del curso")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES, default=YOUTUBE, verbose_name="Tipo de Recurso")
    has_certification = models.BooleanField(default=False, verbose_name="¿Incluye Certificado?")
    

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_courses",
    )
    is_published = models.BooleanField(default=False, verbose_name="Publicado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.title} ({self.category})"