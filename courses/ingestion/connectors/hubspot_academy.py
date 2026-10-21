import logging
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class HubSpotAcademyConnector(BaseCourseConnector):
    """
    Conector para HubSpot Academy.
    Cursos y certificaciones 100% gratuitas con credencial oficial verificable.
    Especialmente relevante para Ingeniería Industrial (CRM, Automatización de Procesos de Negocio,
    Gestión Comercial, Analítica y Productividad Organizacional).
    """
    platform_id = "hubspot"
    platform_name = "HubSpot Academy"
    tier = 1
    group = "industrial"

    CERTIFICATIONS_CATALOG = [
        {
            "id": "hubspot-crm-operations",
            "title": "Certificación en Automatización y Operaciones CRM",
            "url": "https://academy.hubspot.com/courses/hubspot-crm-operations",
            "description": "Aprende a diseñar flujos de trabajo automatizados, gestión de datos maestros, sincronización de operaciones comerciales e integración con herramientas ERP.",
            "level": "intermediate",
            "duration_hours": 4.5,
            "tags": ["CRM", "Automatización", "Operaciones", "Procesos", "Flujos de Trabajo"],
            "career_hints": ["industrial", "sistemas"],
        },
        {
            "id": "inbound-sales-processes",
            "title": "Certificación en Gestión de Procesos Comerciales y Ventas Inbound",
            "url": "https://academy.hubspot.com/courses/inbound-sales",
            "description": "Optimización del embudo de operaciones comerciales, identificación de prospectos, calificación de clientes y estandarización del proceso comercial.",
            "level": "beginner",
            "duration_hours": 3.5,
            "tags": ["Ventas", "Operaciones Comerciales", "Gestión de Procesos", "Productividad"],
            "career_hints": ["industrial"],
        },
        {
            "id": "revenue-operations-revops",
            "title": "Certificación en Revenue Operations (RevOps)",
            "url": "https://academy.hubspot.com/courses/revenue-operations",
            "description": "Estrategia integral de Revenue Operations: alineación de procesos entre marketing, ventas y servicio postventa para maximizar la eficiencia y reducir cuellos de botella.",
            "level": "advanced",
            "duration_hours": 5.0,
            "tags": ["RevOps", "Optimización de Procesos", "Productividad", "KPIs"],
            "career_hints": ["industrial", "sistemas"],
        },
        {
            "id": "frictionless-sales-pipeline",
            "title": "Optimización del Pipeline de Ventas sin Fricciones",
            "url": "https://academy.hubspot.com/courses/frictionless-sales",
            "description": "Técnicas de ingeniería y optimización para eliminar fricciones y pérdidas de tiempo en el ciclo de vida del cliente y la cadena de valor.",
            "level": "intermediate",
            "duration_hours": 2.5,
            "tags": ["Lean", "Fricción de Procesos", "Pipeline", "Cadena de Valor"],
            "career_hints": ["industrial"],
        },
        {
            "id": "marketing-automation-analytics",
            "title": "Automatización de Marketing y Analítica de Datos",
            "url": "https://academy.hubspot.com/courses/marketing-automation",
            "description": "Configuración de reglas de negocio, segmentación predictiva, triggers de eventos y métricas de atribución para toma de decisiones orientada a datos.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Automatización", "Analítica", "Métricas", "Reglas de Negocio"],
            "career_hints": ["industrial", "sistemas"],
        },
        {
            "id": "service-hub-customer-success",
            "title": "Gestión de Servicio al Cliente y Calidad Operativa",
            "url": "https://academy.hubspot.com/courses/service-hub-software",
            "description": "Gestión de SLAs (Acuerdos de Nivel de Servicio), Help Desk automatizado, encuestas CSAT y gestión de calidad del servicio.",
            "level": "beginner",
            "duration_hours": 3.0,
            "tags": ["SLA", "Calidad de Servicio", "Help Desk", "Satisfacción del Cliente"],
            "career_hints": ["industrial"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando certificaciones oficiales de HubSpot Academy...")

        items = self.CERTIFICATIONS_CATALOG
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"hubspot-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://www.hubspot.com/hubfs/assets/hubspot.com/style-guide/module-images/hubspot-logo.svg",
                    language="es",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=item["duration_hours"],
                    instructor_name="HubSpot Academy",
                    category_hint="Gestión de Procesos & Calidad",
                    tags=item["tags"],
                    provider_name="HubSpot",
                    credential_type="certificate",
                    is_free_credential=True,
                    has_practical_labs=False,
                    career_hints=item.get("career_hints", ["industrial"])
                )
            )

        logger.info("HubSpot Academy: %d certificaciones procesadas con éxito", len(courses))
        return courses
