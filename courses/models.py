from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=80, verbose_name="Nombre de la Categoría")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="Tecnología")

    class Meta:
        verbose_name = "Tecnología"
        verbose_name_plural = "Tecnologías"

    def __str__(self):
        return self.name

    def clean(self):
        if Tag.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Esta tecnología ya existe.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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

    YOUTUBE = "youtube"
    PLATFORM = "platform"
    DOCS = "docs"
    RESOURCE_CHOICES = [
        (YOUTUBE, "Lista de YouTube"),
        (PLATFORM, "Plataforma Web"),
        (DOCS, "Documentación / Lectura"),
    ]

    title = models.CharField(max_length=120, verbose_name="Título del Curso")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="Descripción Corta")
    description = models.TextField(blank=True, verbose_name="Descripción Detallada")
    
    # RELACIONES MEJORADAS PARA FILTROS
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Categoría Temática"
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tecnologías")
    
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
        # Forma más segura de manejar las categorías vacías
        if self.category:
            return f"{self.title} ({self.category.name})"
        return f"{self.title} (Sin categoría)"