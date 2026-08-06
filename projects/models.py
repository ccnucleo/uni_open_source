from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(upload_to="technologies/icons/", blank=True, null=True)
    
    def __str__(self): return self.name

    def clean(self):
        if Technology.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Esta tecnología ya existe.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Project(models.Model):
    title = models.CharField(max_length=120)
    summary = models.CharField(max_length=255, verbose_name="Descripción Breve (Hero)")
    description = models.TextField(blank=True, verbose_name="Descripción detallada")

    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    # NUEVO CAMPO PARA DOCUMENTACIÓN
    documentation_file = models.FileField(upload_to="projects/docs/", blank=True, null=True)
    
    repository_url = models.URLField(blank=True)
    version = models.CharField(max_length=20, default="v1.0.0")
    size = models.CharField(max_length=20, blank=True)
    dependencies = models.TextField(blank=True)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="collaborated_projects", blank=True)
    is_public = models.BooleanField(default=True)
    
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_projects", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="projects/gallery/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']