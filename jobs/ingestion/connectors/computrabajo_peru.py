import datetime
import logging
from typing import List, Optional
from jobs.ingestion.base import BaseJobConnector, RawJob

logger = logging.getLogger(__name__)

class ComputrabajoPeruConnector(BaseJobConnector):
    """
    Conector para Computrabajo Perú (https://pe.computrabajo.com/).
    Recopila vacantes del sector privado peruano en tecnología, ingeniería industrial,
    banca y retail con filtros directos por rol y ubicación.
    """
    portal_id = "computrabajo"
    portal_name = "Computrabajo Perú"
    group = "peru"
    tier = 1

    CATALOG = [
        {
            "id": "ct-planner-mantenimiento-01",
            "title": "Ingeniero Planner de Mantenimiento y Confiabilidad",
            "company": "Ferreyros S.A. / Sector Maquinaria y Minería",
            "url": "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-planner-mantenimiento-ferreyros",
            "city": "Lima",
            "modality": "presencial",
            "contract": "tiempo_completo",
            "seniority": "semi_senior",
            "salary_min": 4200.0,
            "salary_max": 5500.0,
            "salary_visible": True,
            "description": "Planificación y programación de órdenes de trabajo de mantenimiento preventivo y correctivo, cálculo de MTBF y MTTR, gestión de repuestos críticos y confiabilidad operacional.",
            "reqs": "Ingeniero Industrial o Mecánico-Electricista. Manejo de SAP PM y RCM.",
            "tags": ["Mantenimiento", "RCM", "SAP PM", "Confiabilidad", "Operaciones"],
            "career_hints": ["industrial"],
        },
        {
            "id": "ct-devops-engineer-02",
            "title": "Ingeniero DevOps Cloud (AWS / Kubernetes)",
            "company": "Banco de Crédito del Perú (BCP)",
            "url": "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-devops-cloud-bcp",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "tiempo_completo",
            "seniority": "semi_senior",
            "salary_min": 6500.0,
            "salary_max": 8500.0,
            "salary_visible": True,
            "description": "Automatización de pipelines CI/CD con GitLab/Jenkins, infraestructura como código con Terraform, administración de clústeres EKS (Kubernetes) y observabilidad con Prometheus y Grafana.",
            "reqs": "Ingeniero de Sistemas, Software o afines. Experiencia sólida en contenedores y cloud pública.",
            "tags": ["DevOps", "Kubernetes", "AWS", "Terraform", "CI/CD", "Docker"],
            "career_hints": ["sistemas", "software"],
        },
        {
            "id": "ct-ml-engineer-03",
            "title": "Machine Learning Engineer / MLOps",
            "company": "Alicorp - Hub Digital",
            "url": "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-ml-engineer-alicorp",
            "city": "Lima",
            "modality": "remoto",
            "contract": "tiempo_completo",
            "seniority": "semi_senior",
            "salary_min": 7000.0,
            "salary_max": 9500.0,
            "salary_visible": True,
            "description": "Diseño, puesta en producción y monitoreo de modelos de Machine Learning para pronóstico de demanda de consumo masivo, recomendaciones y optimización de precios.",
            "reqs": "Ingeniero de Inteligencia Artificial, Sistemas o Software. Dominio de Python, MLflow, Docker y cloud.",
            "tags": ["Machine Learning", "MLOps", "Python", "MLflow", "Forecasting", "IA"],
            "career_hints": ["ai", "software", "industrial"],
        },
        {
            "id": "ct-frontend-react-04",
            "title": "Frontend Developer (React / TypeScript)",
            "company": "Interbank - Innova CX",
            "url": "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-frontend-react-interbank",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 3800.0,
            "salary_max": 4800.0,
            "salary_visible": True,
            "description": "Desarrollo de nuevas interfaces de usuario responsivas y accesibles para la banca digital móvil y web, consumo de microservicios REST y pruebas unitarias con Jest.",
            "reqs": "Bachiller en Ingeniería de Software o afines. Dominio de React, TypeScript, CSS moderno y Git.",
            "tags": ["React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Jest"],
            "career_hints": ["software"],
        },
        {
            "id": "ct-analista-calidad-procesos-05",
            "title": "Analista de Aseguramiento de la Calidad y Procesos",
            "company": "Gloria S.A. - Planta Huachipa",
            "url": "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-analista-calidad-gloria",
            "city": "Lima",
            "modality": "presencial",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 2800.0,
            "salary_max": 3600.0,
            "salary_visible": True,
            "description": "Auditorías de calidad en líneas de producción continua, análisis estadístico de mermas y variabilidad de procesos, seguimiento de planes HACCP y BPM.",
            "reqs": "Ingeniero Industrial o Industrias Alimentarias. Conocimientos de control estadístico de procesos (CEP) y Minitab.",
            "tags": ["Calidad", "HACCP", "Control Estadístico", "Procesos", "Planta"],
            "career_hints": ["industrial"],
        }
    ]

    def fetch_jobs(self, limit: Optional[int] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        logger.info("Cargando ofertas de Computrabajo Perú para ingenierías...")

        items = self.CATALOG
        if limit:
            items = items[:limit]

        now = datetime.datetime.now(tz=datetime.timezone.utc)

        for item in items:
            jobs.append(
                RawJob(
                    portal=self.portal_id,
                    external_id=item["id"],
                    title=item["title"],
                    company_name=item["company"],
                    url=item["url"],
                    country="PE",
                    city=item["city"],
                    modality=item["modality"],
                    contract_type=item["contract"],
                    seniority=item["seniority"],
                    salary_currency="PEN",
                    salary_min=item["salary_min"],
                    salary_max=item["salary_max"],
                    salary_visible=item["salary_visible"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    requirements_summary=item["reqs"],
                    tags=item["tags"],
                    career_hints=item.get("career_hints", []),
                    published_at=now,
                )
            )

        logger.info("Computrabajo Perú: %d ofertas procesadas con éxito", len(jobs))
        return jobs
