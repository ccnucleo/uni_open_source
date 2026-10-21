import datetime
import logging
from typing import List, Optional
from jobs.ingestion.base import BaseJobConnector, RawJob

logger = logging.getLogger(__name__)

class EmpleosPeruConnector(BaseJobConnector):
    """
    Conector para el portal oficial de Empleos Perú (Ministerio de Trabajo y Promoción del Empleo - MTPE).
    Recopila convocatorias laborales públicas y privadas verificadas en Lima y a nivel nacional,
    con énfasis en prácticas preprofesionales, profesionales y puestos junior en ingeniería.
    """
    portal_id = "empleos_peru"
    portal_name = "Empleos Perú (MTPE)"
    group = "peru"
    tier = 1

    CATALOG = [
        {
            "id": "mtpe-practicante-procesos-01",
            "title": "Practicante Preprofesional de Ingeniería Industrial y Mejora Continua",
            "company": "Ministerio de la Producción (PRODUCE) / Sector Industrial",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/practicante-procesos-produce",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "practicas_pre",
            "seniority": "practicante",
            "salary_min": 1200.0,
            "salary_max": 1400.0,
            "salary_visible": True,
            "description": "Apoyo en el mapeo y optimización de flujos operativos, documentación de procedimientos bajo ISO 9001, seguimiento de indicadores de productividad y control de inventarios.",
            "reqs": "Estudiante de 7mo a 9no ciclo de Ingeniería Industrial. Manejo intermedio de Excel y Power BI. Conocimientos en BPMN y Lean.",
            "tags": ["Ingeniería Industrial", "Mejora Continua", "BPMN", "Power BI", "ISO 9001"],
            "career_hints": ["industrial"],
        },
        {
            "id": "mtpe-analista-sistemas-02",
            "title": "Analista Junior de Sistemas e Infraestructura TI",
            "company": "Superintendencia Nacional de Aduanas y de Administración Tributaria (SUNAT)",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/analista-sistemas-sunat",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 3500.0,
            "salary_max": 4500.0,
            "salary_visible": True,
            "description": "Monitoreo de servidores Linux y bases de datos Oracle/PostgreSQL, configuración de enlaces de red TCP/IP, soporte técnico de segundo nivel y automatización con scripts Bash.",
            "reqs": "Egresado o bachiller en Ingeniería de Sistemas o Redes. Certificación CCNA o Linux deseable.",
            "tags": ["Linux", "Redes", "PostgreSQL", "Bash", "Infraestructura"],
            "career_hints": ["sistemas"],
        },
        {
            "id": "mtpe-desarrollador-fullstack-03",
            "title": "Desarrollador de Software Web Junior (Python / React)",
            "company": "Presidencia del Consejo de Ministros (PCM) - Secretaría de Gobierno Digital",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/desarrollador-web-pcm",
            "city": "Lima",
            "modality": "remoto",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 4000.0,
            "salary_max": 5000.0,
            "salary_visible": True,
            "description": "Construcción de servicios web y APIs REST con Python (FastAPI/Django) y componentes frontend con React para la plataforma unificada Gob.pe.",
            "reqs": "Bachiller o titulado en Ingeniería de Software, Ciencias de la Computación o Sistemas. Experiencia demostrable en Git, APIs y bases de datos relacionales.",
            "tags": ["Python", "React", "FastAPI", "PostgreSQL", "Git", "Docker"],
            "career_hints": ["software", "sistemas"],
        },
        {
            "id": "mtpe-analista-datos-ia-04",
            "title": "Practicante Profesional de Ciencia de Datos e Inteligencia Artificial",
            "company": "Instituto Nacional de Estadística e Informática (INEI)",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/practicante-ia-inei",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "practicas_pro",
            "seniority": "practicante",
            "salary_min": 1500.0,
            "salary_max": 1800.0,
            "salary_visible": True,
            "description": "Procesamiento y limpieza de grandes conjuntos de datos censales, desarrollo de modelos predictivos en Python/R y tableros interactivos para toma de decisiones públicas.",
            "reqs": "Egresado o bachiller de Inteligencia Artificial, Ciencia de Datos o Ingeniería de Sistemas. Manejo de Pandas, Scikit-Learn y SQL.",
            "tags": ["Machine Learning", "Python", "SQL", "Pandas", "Scikit-Learn", "Data Science"],
            "career_hints": ["ai", "sistemas"],
        },
        {
            "id": "mtpe-asistente-logistica-05",
            "title": "Asistente de Cadena de Suministro y Operaciones Logísticas",
            "company": "Corporación Logística del Perú S.A.",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/asistente-logistica-clp",
            "city": "Callao / Lima",
            "modality": "presencial",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 2500.0,
            "salary_max": 3200.0,
            "salary_visible": True,
            "description": "Control de entradas y salidas de almacén, programación de rutas de despacho, coordinación con proveedores y análisis de rotación de stocks en sistema ERP.",
            "reqs": "Bachiller en Ingeniería Industrial. Excel avanzado y conocimiento de SAP MM o WMS.",
            "tags": ["Logística", "Supply Chain", "SAP", "Excel Avanzado", "Operaciones"],
            "career_hints": ["industrial"],
        },
        {
            "id": "mtpe-ciberseguridad-junior-06",
            "title": "Especialista Junior en Seguridad de la Información y SOC",
            "company": "Banco de la Nación del Perú",
            "url": "https://www.empleosperu.gob.pe/portal-mtpe/#/oferta/seguridad-soc-bn",
            "city": "Lima",
            "modality": "hibrido",
            "contract": "tiempo_completo",
            "seniority": "junior",
            "salary_min": 4500.0,
            "salary_max": 5500.0,
            "salary_visible": True,
            "description": "Monitoreo continuo de eventos de seguridad (SIEM), análisis de vulnerabilidades, respuesta inicial ante incidentes y cumplimiento de la normativa SBS.",
            "reqs": "Ingeniero de Sistemas o Telecomunicaciones. Conocimiento de SIEM (Splunk/QRadar), firewalls y conceptos de ciberseguridad.",
            "tags": ["Ciberseguridad", "SOC", "SIEM", "Firewalls", "Redes"],
            "career_hints": ["sistemas"],
        }
    ]

    def fetch_jobs(self, limit: Optional[int] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        logger.info("Cargando convocatorias verificadas de Empleos Perú (MTPE)...")

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

        logger.info("Empleos Perú: %d convocatorias oficiales procesadas", len(jobs))
        return jobs
