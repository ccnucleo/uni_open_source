import logging
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class GoogleSkillsConnector(BaseCourseConnector):
    """
    Conector para Google Skills / Cloud Skills Boost (https://www.skills.google/).
    Rutas de aprendizaje oficiales con laboratorios prácticos en Google Cloud Platform
    y Skill Badges verificables para IA, Machine Learning, Cloud Architecture, Big Data y DevOps.
    """
    platform_id = "google_skills"
    platform_name = "Google Skills / Cloud Skills Boost"
    tier = 1
    group = "cloud"

    PATHS = [
        {
            "id": "ml-engineer-path-17",
            "title": "Machine Learning Engineer Learning Path",
            "url": "https://www.skills.google/paths/17",
            "description": "Ruta profesional oficial de Google Cloud para ingenieros de ML: Vertex AI, BigQuery ML, canalizaciones de MLOps con TensorFlow y despliegue de modelos a escala.",
            "level": "advanced",
            "duration_hours": 32.0,
            "tags": ["Machine Learning", "Vertex AI", "BigQuery ML", "MLOps", "TensorFlow", "Google Cloud"],
            "career_hints": ["ia", "software", "sistemas"],
        },
        {
            "id": "gen-ai-for-developers",
            "title": "Generative AI for Developers Path",
            "url": "https://www.skills.google/course_templates/536",
            "description": "Desarrollo de aplicaciones inteligentes con Gemini API, modelos fundacionales de Vertex AI Studio, LangChain y arquitecturas RAG (Retrieval-Augmented Generation).",
            "level": "intermediate",
            "duration_hours": 15.0,
            "tags": ["Generative AI", "Gemini", "Vertex AI", "RAG", "LLMs", "Python"],
            "career_hints": ["ia", "software"],
        },
        {
            "id": "cloud-architect-path",
            "title": "Cloud Architect Learning Path",
            "url": "https://www.skills.google/paths/12",
            "description": "Diseño de infraestructuras empresariales escalables y resilientes en Google Cloud: VPCs, Kubernetes Engine (GKE), Cloud Run, balanceo de carga y alta disponibilidad.",
            "level": "advanced",
            "duration_hours": 40.0,
            "tags": ["Google Cloud", "GKE", "Kubernetes", "Cloud Architecture", "Redes", "VPC"],
            "career_hints": ["sistemas", "software"],
        },
        {
            "id": "devops-engineer-path",
            "title": "Cloud DevOps & SRE Learning Path",
            "url": "https://www.skills.google/paths/16",
            "description": "Prácticas de Site Reliability Engineering (SRE), integración y entrega continua (CI/CD) con Cloud Build, monitorización con Cloud Operations (Stackdriver) e infraestructura como código con Terraform.",
            "level": "intermediate",
            "duration_hours": 28.0,
            "tags": ["DevOps", "SRE", "Terraform", "CI/CD", "Cloud Build", "Monitoreo"],
            "career_hints": ["sistemas", "software"],
        },
        {
            "id": "data-analyst-path",
            "title": "Data Analyst & Big Data Path",
            "url": "https://www.skills.google/paths/15",
            "description": "Almacenamiento de datos analíticos masivos con BigQuery, visualización interactiva con Looker Studio y preparación de datos para analítica de negocios e ingeniería de procesos.",
            "level": "beginner",
            "duration_hours": 24.0,
            "tags": ["BigQuery", "SQL", "Looker", "Data Analytics", "ETL"],
            "career_hints": ["industrial", "ia", "sistemas"],
        },
        {
            "id": "cloud-security-engineer-path",
            "title": "Cloud Security Engineer Learning Path",
            "url": "https://www.skills.google/paths/14",
            "description": "Seguridad defensiva en la nube: gestión granular de identidades (IAM), Cloud KMS, protección contra amenazas con Security Command Center y cumplimiento normativo.",
            "level": "intermediate",
            "duration_hours": 25.0,
            "tags": ["Cloud Security", "IAM", "KMS", "Compliance", "Seguridad"],
            "career_hints": ["sistemas"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando rutas oficiales de Google Skills...")

        items = self.PATHS
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"gs-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://www.gstatic.com/devrel-devsite/prod/v9e8fdf0b07e7fb1faaa90ab5daea3cc692e15bc3283626e25539fa953bc9d634/cloud/images/cloud-logo.svg",
                    language="en",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=item["duration_hours"],
                    instructor_name="Google Cloud Training",
                    category_hint="Cloud Computing & DevOps",
                    tags=item["tags"],
                    provider_name="Google Cloud",
                    credential_type="skill_badge",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=item.get("career_hints", ["sistemas", "ia"])
                )
            )

        logger.info("Google Skills: %d rutas procesadas con éxito", len(courses))
        return courses
