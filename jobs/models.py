from django.conf import settings
from django.db import models
from django.utils.text import slugify
from courses.models import Career, Tag

class JobListing(models.Model):
    """
    Representa una vacante laboral o práctica profesional recopilada desde portales oficiales.
    Orientada a estudiantes y egresados de Ingeniería Industrial, Sistemas, Software e IA.
    """
    # Portales prioritarios según Detalles páginas.md
    PORTAL_EMPLEOS_PERU = "empleos_peru"
    PORTAL_BOLSA_MTPE = "bolsa_mtpe"
    PORTAL_COMPUTRABAJO = "computrabajo"
    PORTAL_INDEED = "indeed"
    PORTAL_LINKEDIN = "linkedin"
    PORTAL_BUMERAN = "bumeran"
    PORTAL_GLASSDOOR = "glassdoor"
    PORTAL_GETONBRD = "getonbrd"
    PORTAL_REMOTEOK = "remoteok"
    PORTAL_WEWORKREMOTELY = "weworkremotely"
    PORTAL_WELLFOUND = "wellfound"
    PORTAL_OTTA = "otta"
    PORTAL_HACKER_NEWS = "hacker_news"
    PORTAL_GITHUB_CAREERS = "github_careers"
    PORTAL_MANUAL = "manual"
    PORTAL_OTHER = "other"

    PORTAL_CHOICES = [
        (PORTAL_EMPLEOS_PERU, "Empleos Perú (MTPE)"),
        (PORTAL_BOLSA_MTPE, "Bolsa de Trabajo MTPE / VUPE"),
        (PORTAL_COMPUTRABAJO, "Computrabajo Perú"),
        (PORTAL_INDEED, "Indeed Perú"),
        (PORTAL_LINKEDIN, "LinkedIn Empleos Perú"),
        (PORTAL_BUMERAN, "Bumeran Perú"),
        (PORTAL_GLASSDOOR, "Glassdoor"),
        (PORTAL_GETONBRD, "Get on Board (Tech LatAm)"),
        (PORTAL_REMOTEOK, "RemoteOK (Tech Remoto)"),
        (PORTAL_WEWORKREMOTELY, "We Work Remotely"),
        (PORTAL_WELLFOUND, "Wellfound (Startups)"),
        (PORTAL_OTTA, "Otta"),
        (PORTAL_HACKER_NEWS, "Hacker News (Who is Hiring)"),
        (PORTAL_GITHUB_CAREERS, "GitHub Careers"),
        (PORTAL_MANUAL, "Publicación Manual UNI"),
        (PORTAL_OTHER, "Otro Portal"),
    ]

    MODALITY_REMOTE = "remoto"
    MODALITY_HYBRID = "hibrido"
    MODALITY_ON_SITE = "presencial"
    MODALITY_CHOICES = [
        (MODALITY_REMOTE, "Remoto"),
        (MODALITY_HYBRID, "Híbrido"),
        (MODALITY_ON_SITE, "Presencial"),
    ]

    CONTRACT_FULL_TIME = "tiempo_completo"
    CONTRACT_PART_TIME = "medio_tiempo"
    CONTRACT_PRACTICAS_PRE = "practicas_pre"
    CONTRACT_PRACTICAS_PRO = "practicas_pro"
    CONTRACT_FREELANCE = "freelance"
    CONTRACT_TEMPORAL = "temporal"
    CONTRACT_CHOICES = [
        (CONTRACT_FULL_TIME, "Tiempo Completo"),
        (CONTRACT_PART_TIME, "Medio Tiempo"),
        (CONTRACT_PRACTICAS_PRE, "Prácticas Preprofesionales"),
        (CONTRACT_PRACTICAS_PRO, "Prácticas Profesionales"),
        (CONTRACT_FREELANCE, "Freelance / Proyecto"),
        (CONTRACT_TEMPORAL, "Temporal"),
    ]

    SENIORITY_INTERN = "practicante"
    SENIORITY_JUNIOR = "junior"
    SENIORITY_SEMI_SENIOR = "semi_senior"
    SENIORITY_SENIOR = "senior"
    SENIORITY_LEAD = "lead"
    SENIORITY_CHOICES = [
        (SENIORITY_INTERN, "Practicante"),
        (SENIORITY_JUNIOR, "Junior"),
        (SENIORITY_SEMI_SENIOR, "Semi-Senior"),
        (SENIORITY_SENIOR, "Senior"),
        (SENIORITY_LEAD, "Lead / Arquitecto"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activa"),
        (STATUS_EXPIRED, "Expirada"),
        (STATUS_DRAFT, "Borrador"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título del Puesto")
    slug = models.SlugField(max_length=230, unique=True, verbose_name="Slug amigable")
    company_name = models.CharField(max_length=150, verbose_name="Empresa / Organización")
    company_logo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Logo de la Empresa")

    portal = models.CharField(max_length=50, choices=PORTAL_CHOICES, default=PORTAL_OTHER, verbose_name="Portal de Origen")
    external_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID Externo")
    url = models.URLField(max_length=500, verbose_name="Enlace Oficial a la Vacante")

    country = models.CharField(max_length=50, default="PE", verbose_name="País")
    city = models.CharField(max_length=100, blank=True, default="Lima", verbose_name="Ciudad / Región")
    modality = models.CharField(max_length=30, choices=MODALITY_CHOICES, default=MODALITY_REMOTE, verbose_name="Modalidad")
    contract_type = models.CharField(max_length=40, choices=CONTRACT_CHOICES, default=CONTRACT_FULL_TIME, verbose_name="Tipo de Contrato")
    seniority = models.CharField(max_length=30, choices=SENIORITY_CHOICES, default=SENIORITY_JUNIOR, verbose_name="Nivel de Experiencia")

    careers = models.ManyToManyField(Career, blank=True, related_name="job_listings", verbose_name="Carreras de Ingeniería Afines")
    tags = models.ManyToManyField(Tag, blank=True, related_name="job_listings", verbose_name="Tecnologías / Habilidades")

    # Información salarial referencial
    salary_currency = models.CharField(max_length=10, blank=True, default="PEN", verbose_name="Moneda")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salario Mínimo")
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salario Máximo")
    salary_visible = models.BooleanField(default=False, verbose_name="¿Salario Visible?")

    short_description = models.CharField(max_length=300, blank=True, verbose_name="Resumen de la Vacante")
    description = models.TextField(blank=True, verbose_name="Descripción del Puesto y Requisitos")
    requirements_summary = models.TextField(blank=True, verbose_name="Requisitos Principales")

    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Publicación")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cierre / Expiración")
    last_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Última Verificación")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name="Estado")

    content_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="Hash de Contenido (SHA-256)")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Vistas")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Vacante de Empleo"
        verbose_name_plural = "Vacantes de Empleo"
        constraints = [
            models.UniqueConstraint(
                fields=["portal", "external_id"],
                name="unique_portal_job",
                condition=models.Q(external_id__isnull=False) & ~models.Q(external_id=""),
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.company_name} ({self.get_portal_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company_name}-{self.title}")[:200]
            self.slug = base_slug
        super().save(*args, **kwargs)

    @property
    def salary_display(self):
        if not self.salary_visible:
            return "No especificado"
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        if self.salary_min:
            return f"Desde {self.salary_currency} {self.salary_min:,.0f}"
        if self.salary_max:
            return f"Hasta {self.salary_currency} {self.salary_max:,.0f}"
        return "A convenir"


class JobBookmark(models.Model):
    """
    Permite a los estudiantes guardar, hacer seguimiento y registrar su postulación
    a las vacantes de su interés.
    """
    STATUS_SAVED = "guardado"
    STATUS_APPLIED = "postulado"
    STATUS_IN_PROCESS = "en_proceso"
    STATUS_OFFER = "oferta"
    STATUS_DISCARDED = "descartado"
    STATUS_CHOICES = [
        (STATUS_SAVED, "Guardado para después"),
        (STATUS_APPLIED, "Postulación enviada"),
        (STATUS_IN_PROCESS, "En proceso de entrevista"),
        (STATUS_OFFER, "Oferta recibida"),
        (STATUS_DISCARDED, "Descartado"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarked_jobs", verbose_name="Estudiante")
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="Vacante")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_SAVED, verbose_name="Estado de Seguimiento")
    notes = models.TextField(blank=True, verbose_name="Notas personales")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Seguimiento de Vacante"
        verbose_name_plural = "Seguimiento de Vacantes"
        constraints = [
            models.UniqueConstraint(fields=["user", "job"], name="unique_user_job_bookmark")
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.job.title} ({self.get_status_display()})"


class JobSyncAuditLog(models.Model):
    """
    Registro de auditoría técnica de cada sincronización e ingesta de vacantes.
    """
    STATUS_SUCCESS = "success"
    STATUS_WARNING = "warning"
    STATUS_ERROR = "error"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Éxito"),
        (STATUS_WARNING, "Advertencia"),
        (STATUS_ERROR, "Error"),
    ]

    portal = models.CharField(max_length=50, verbose_name="Portal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS, verbose_name="Estado")
    jobs_fetched = models.PositiveIntegerField(default=0, verbose_name="Obtenidas")
    jobs_created = models.PositiveIntegerField(default=0, verbose_name="Creadas")
    jobs_updated = models.PositiveIntegerField(default=0, verbose_name="Actualizadas")
    jobs_unchanged = models.PositiveIntegerField(default=0, verbose_name="Sin cambios")
    errors_count = models.PositiveIntegerField(default=0, verbose_name="Errores")
    duration_seconds = models.FloatField(default=0.0, verbose_name="Duración (segundos)")
    details = models.TextField(blank=True, verbose_name="Detalles / Log de salida")
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    class Meta:
        ordering = ["-executed_at"]
        verbose_name = "Auditoría de Ingesta de Empleos"
        verbose_name_plural = "Auditorías de Ingesta de Empleos"

    def __str__(self):
        return f"[{self.executed_at.strftime('%Y-%m-%d %H:%M')}] {self.portal} - {self.get_status_display()}"
