from django.conf import settings
from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Project(models.Model):
    THEME_CHOICES = [
        ("web", "Desarrollo Web"),
        ("mobile", "Apps Móviles"),
        ("ia", "IA / Machine Learning"),
        ("data", "Data Science"),
        ("iot", "IoT"),
        ("games", "Videojuegos"),
        ("security", "Seguridad"),
        ("api", "APIs / Backend"),
        ("devops", "DevOps"),
        ("research", "Investigación"),
    ]

    title = models.CharField(max_length=120)
    summary = models.CharField(max_length=255, verbose_name="Descripción Breve (Hero)")
    
    paragraph_1 = models.TextField(blank=True, verbose_name="Sección 1: Contexto/Problema")
    paragraph_2 = models.TextField(blank=True, verbose_name="Sección 2: Funcionalidades")
    paragraph_3 = models.TextField(blank=True, verbose_name="Sección 3: Detalles Técnicos")

    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="web")
    main_tech = models.CharField(max_length=50, verbose_name="Tecnología Principal")
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    repository_url = models.URLField(blank=True)
    version = models.CharField(max_length=20, default="v1.0.0")
    size = models.CharField(max_length=20, blank=True)
    dependencies = models.TextField(blank=True)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="collaborated_projects", blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def tech_stack(self):
        return self.main_tech

    @tech_stack.setter
    def tech_stack(self, value):
        self.main_tech = value or ""

    @property
    def description(self):
        return self.paragraph_1 or self.summary

    @description.setter
    def description(self, value):
        val = value or ""
        self.paragraph_1 = val
        if not self.summary:
            self.summary = val[:255]

    @property
    def demo_url(self):
        return ""

    @demo_url.setter
    def demo_url(self, value):
        pass

    @property
    def image_url(self):
        return self.image.url if self.image else None



class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="projects/gallery/")