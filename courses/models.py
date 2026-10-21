from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify # <-- Importación nueva para generar URLs amigables

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

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

class Career(models.Model):
    """
    Representa una carrera profesional de ingeniería para clasificar los recursos de aprendizaje.
    """
    INDUSTRIAL = "industrial"
    SYSTEMS = "systems"
    SOFTWARE = "software"
    AI = "ai"

    CODE_CHOICES = [
        (INDUSTRIAL, "Ingeniería Industrial"),
        (SYSTEMS, "Ingeniería de Sistemas"),
        (SOFTWARE, "Ingeniería de Software"),
        (AI, "Inteligencia Artificial"),
    ]

    code = models.CharField(max_length=30, unique=True, choices=CODE_CHOICES, verbose_name="Código de Carrera")
    name = models.CharField(max_length=100, verbose_name="Nombre de la Carrera")
    icon = models.CharField(max_length=50, blank=True, default="fa-graduation-cap", verbose_name="Ícono FontAwesome")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Carrera de Ingeniería"
        verbose_name_plural = "Carreras de Ingeniería"

    def __str__(self):
        return self.name

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
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, verbose_name="Slug (URL dinámica)")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="Descripción Corta")
    description = models.TextField(blank=True, verbose_name="Descripción Detallada")
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Categoría Temática"
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tecnologías")
    careers = models.ManyToManyField(Career, blank=True, related_name="courses", verbose_name="Carreras de Ingeniería")

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER, verbose_name="Nivel")
    url = models.URLField(max_length=500, blank=True, verbose_name="Enlace al curso gratuito")
    image = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True, verbose_name="Imagen del curso")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES, default=YOUTUBE, verbose_name="Tipo de Recurso")
    has_certification = models.BooleanField(default=False, verbose_name="¿Incluye Certificado?")
    
    # Credenciales y laboratorios
    CREDENTIAL_SKILL_BADGE = "skill_badge"
    CREDENTIAL_CERTIFICATE = "certificate"
    CREDENTIAL_AUDIT = "audit_access"
    CREDENTIAL_COMPLETION = "completion"
    CREDENTIAL_NONE = "none"

    CREDENTIAL_TYPE_CHOICES = [
        (CREDENTIAL_NONE, "Sin credencial formal"),
        (CREDENTIAL_CERTIFICATE, "Certificado Gratuito"),
        (CREDENTIAL_SKILL_BADGE, "Skill Badge / Insignia"),
        (CREDENTIAL_COMPLETION, "Constancia de Finalización"),
        (CREDENTIAL_AUDIT, "Acceso Gratuito (Auditoría)"),
    ]
    credential_type = models.CharField(
        max_length=30,
        choices=CREDENTIAL_TYPE_CHOICES,
        default=CREDENTIAL_NONE,
        verbose_name="Tipo de Credencial"
    )
    is_free_credential = models.BooleanField(default=True, verbose_name="¿Credencial 100% Gratuita?")
    has_practical_labs = models.BooleanField(default=False, verbose_name="¿Incluye Laboratorios Prácticos?")
    provider_name = models.CharField(max_length=100, blank=True, verbose_name="Proveedor / Empresa")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_courses",
        null=True,
        blank=True,
        verbose_name="Propietario / Creador"
    )
    is_published = models.BooleanField(default=True, verbose_name="Publicado")
    
    # CAMPOS DE AUTOMATIZACIÓN Y SINCRONIZACIÓN
    MANUAL = "manual"
    FREECODECAMP = "freecodecamp"
    MIT_OCW = "mit_ocw"
    MICROSOFT_LEARN = "microsoft_learn"
    GOOGLE_SKILLS = "google_skills"
    IBM_SKILLS = "ibm"
    AWS_SKILLBUILDER = "aws_skillbuilder"
    KAGGLE = "kaggle"
    HUGGINGFACE = "huggingface"
    HUBSPOT = "hubspot"
    TALENTO_DIGITAL_PCM = "talento_digital_pcm"
    CAPACITAT = "capacitat"
    THE_ODIN_PROJECT = "the_odin_project"
    COURSERA = "coursera"
    EDX = "edx"
    ALISON = "alison"
    DEEPLEARNING_AI = "deeplearning_ai"
    OTHER = "other"

    PLATFORM_SOURCE_CHOICES = [
        (MANUAL, "Manual"),
        (FREECODECAMP, "freeCodeCamp"),
        (MIT_OCW, "Learn with MIT | MIT Learn"),
        (MICROSOFT_LEARN, "Microsoft Learn"),
        (GOOGLE_SKILLS, "Google Skills / Cloud Boost"),
        (IBM_SKILLS, "IBM SkillsBuild / Developer"),
        (AWS_SKILLBUILDER, "AWS Skill Builder"),
        (KAGGLE, "Kaggle Learn"),
        (HUGGINGFACE, "Hugging Face Learn"),
        (HUBSPOT, "HubSpot Academy"),
        (TALENTO_DIGITAL_PCM, "Potencia tu Talento Digital (PCM/Cisco)"),
        (CAPACITAT, "CAPACÍTA-T (MTPE Perú)"),
        (THE_ODIN_PROJECT, "The Odin Project"),
        (COURSERA, "Coursera"),
        (EDX, "edX"),
        (ALISON, "Alison"),
        (DEEPLEARNING_AI, "DeepLearning.AI"),
        (OTHER, "Otro"),
    ]
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_SOURCE_CHOICES,
        default=MANUAL,
        verbose_name="Plataforma de Origen"
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID Externo"
    )
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Hash de Contenido (SHA-256)"
    )
    external_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL de Imagen Externa"
    )
    language = models.CharField(
        max_length=10,
        default="es",
        choices=[("es", "Español"), ("en", "Inglés"), ("other", "Otro")],
        verbose_name="Idioma"
    )
    duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Duración estimada (horas)"
    )
    instructor_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Instructor / Entidad"
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Sincronización"
    )
    STATUS_CHOICES = [
        ("active", "Activo"),
        ("inactive", "Inactivo"),
        ("error", "Error"),
    ]
    sync_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="Estado de Sincronización"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "external_id"],
                name="unique_platform_course",
                condition=models.Q(external_id__isnull=False) & ~models.Q(external_id=""),
            )
        ]


    def __str__(self):
        if self.category:
            return f"{self.title} ({self.category.name})"
        return f"{self.title} (Sin categoría)"

    @property
    def get_image_url(self):
        """
        Retorna la URL de la imagen local si existe, de lo contrario la URL externa.
        """
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.external_image_url:
            return self.external_image_url
        return None

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar automáticamente 
        el slug a partir del título si este no existe.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class SyncAuditLog(models.Model):
    """
    Registro de auditoría para cada ejecución de sincronización e ingesta de cursos.
    """
    STATUS_SUCCESS = "success"
    STATUS_WARNING = "warning"
    STATUS_ERROR = "error"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Éxito"),
        (STATUS_WARNING, "Advertencia"),
        (STATUS_ERROR, "Error"),
    ]

    platform = models.CharField(max_length=50, verbose_name="Plataforma")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS, verbose_name="Estado")
    courses_fetched = models.PositiveIntegerField(default=0, verbose_name="Obtenidos")
    courses_created = models.PositiveIntegerField(default=0, verbose_name="Creados")
    courses_updated = models.PositiveIntegerField(default=0, verbose_name="Actualizados")
    courses_unchanged = models.PositiveIntegerField(default=0, verbose_name="Sin cambios")
    errors_count = models.PositiveIntegerField(default=0, verbose_name="Errores")
    duration_seconds = models.FloatField(default=0.0, verbose_name="Duración (segundos)")
    details = models.TextField(blank=True, verbose_name="Detalles / Log de salida")
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora de ejecución")

    class Meta:
        ordering = ["-executed_at"]
        verbose_name = "Registro de Auditoría de Sincronización"
        verbose_name_plural = "Registros de Auditoría de Sincronización"

    def __str__(self):
        return f"[{self.executed_at.strftime('%Y-%m-%d %H:%M')}] {self.platform} - {self.get_status_display()}"