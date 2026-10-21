import logging
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class TalentoDigitalConnector(BaseCourseConnector):
    """
    Conector para el programa nacional 'Potencia tu Talento Digital'
    (Presidencia del Consejo de Ministros - PCM Perú / Cisco Networking Academy / Skills for All).
    Cursos oficiales 100% gratuitos con insignias digitales y certificados verificables.
    Enfocado en Ingeniería de Sistemas, Redes, Ciberseguridad, IoT y Software.
    """
    platform_id = "talento_digital_pcm"
    platform_name = "Potencia tu Talento Digital (PCM / Cisco)"
    tier = 2
    group = "peru"

    CATALOG = [
        {
            "id": "cisco-intro-cybersecurity",
            "title": "Introducción a la Ciberseguridad",
            "url": "https://skillsforall.com/course/introduction-to-cybersecurity?courseLang=es-XL",
            "description": "Aprende los principios fundamentales de la seguridad informática: amenazas cibernéticas, malware, privacidad en línea y defensa de la infraestructura crítica.",
            "level": "beginner",
            "duration_hours": 6.0,
            "tags": ["Ciberseguridad", "Seguridad Informática", "Redes", "Protección de Datos"],
            "career_hints": ["sistemas", "software"],
        },
        {
            "id": "cisco-networking-basics",
            "title": "Aspectos Básicos de Redes (Networking Basics)",
            "url": "https://skillsforall.com/course/networking-basics?courseLang=es-XL",
            "description": "Comprende la arquitectura de redes de comunicación: modelo TCP/IP, direccionamiento IPv4 e IPv6, conmutadores, enrutadores y conectividad a Internet.",
            "level": "beginner",
            "duration_hours": 22.0,
            "tags": ["Redes", "TCP/IP", "IPv4", "IPv6", "Routing", "Switching"],
            "career_hints": ["sistemas"],
        },
        {
            "id": "cisco-network-devices-setup",
            "title": "Dispositivos de Red e Instalación Inicial",
            "url": "https://skillsforall.com/course/networking-devices-and-initial-configuration?courseLang=es-XL",
            "description": "Configuración inicial de switches y routers Cisco mediante línea de comandos (CLI), seguridad de puertos y administración de interfaces de red.",
            "level": "intermediate",
            "duration_hours": 22.0,
            "tags": ["Cisco CLI", "Configuración de Red", "Switches", "Routers", "Infraestructura"],
            "career_hints": ["sistemas"],
        },
        {
            "id": "cisco-network-defense",
            "title": "Defensa de la Red (Network Defense)",
            "url": "https://skillsforall.com/course/network-defense?courseLang=es-XL",
            "description": "Técnicas avanzadas de defensa perimetral: firewalls, sistemas de detección y prevención de intrusos (IDS/IPS), criptografía y VPNs seguras.",
            "level": "intermediate",
            "duration_hours": 27.0,
            "tags": ["Network Defense", "Firewalls", "VPN", "Criptografía", "Seguridad Perimetral"],
            "career_hints": ["sistemas"],
        },
        {
            "id": "cisco-cyber-threat-management",
            "title": "Gestión de Amenazas Cibernéticas",
            "url": "https://skillsforall.com/course/cyber-threat-management?courseLang=es-XL",
            "description": "Monitoreo de seguridad en centros de operaciones (SOC), análisis de incidentes de seguridad, respuesta ante ataques y análisis forense digital.",
            "level": "advanced",
            "duration_hours": 16.0,
            "tags": ["SOC", "Threat Hunting", "Incident Response", "Forense Digital"],
            "career_hints": ["sistemas"],
        },
        {
            "id": "cisco-python-essentials-1",
            "title": "Fundamentos de Python 1 (Python Essentials 1)",
            "url": "https://skillsforall.com/course/python-essentials-1?courseLang=es-XL",
            "description": "Programación moderna en Python: variables, operadores aritméticos, estructuras de control de flujo condicionales y repetitivas, listas y funciones.",
            "level": "beginner",
            "duration_hours": 30.0,
            "tags": ["Python", "Programación", "Algoritmos", "Lógica"],
            "career_hints": ["software", "ia", "sistemas"],
        },
        {
            "id": "cisco-python-essentials-2",
            "title": "Fundamentos de Python 2 (Programación Orientada a Objetos)",
            "url": "https://skillsforall.com/course/python-essentials-2?courseLang=es-XL",
            "description": "Profundización en Python: Programación Orientada a Objetos (POO), manejo de excepciones, manipulación de archivos y procesamiento de cadenas.",
            "level": "intermediate",
            "duration_hours": 40.0,
            "tags": ["Python", "POO", "Excepciones", "Generadores", "Software"],
            "career_hints": ["software", "ia", "sistemas"],
        },
        {
            "id": "cisco-javascript-essentials-1",
            "title": "Fundamentos de JavaScript 1",
            "url": "https://skillsforall.com/course/javascript-essentials-1?courseLang=es-XL",
            "description": "Desarrollo frontend con JavaScript estándar: variables, tipos de datos primitivos, operadores lógicos, funciones de orden superior y depuración.",
            "level": "beginner",
            "duration_hours": 40.0,
            "tags": ["JavaScript", "Frontend", "Web", "Programación"],
            "career_hints": ["software"],
        },
        {
            "id": "cisco-iot-fundamentals",
            "title": "Introducción a Internet de las Cosas (IoT) y Transformación Digital",
            "url": "https://skillsforall.com/course/introduction-to-iot?courseLang=es-XL",
            "description": "Sensores, actuadores, computación en la niebla (Fog Computing), automatización industrial y convergencia de IT con OT.",
            "level": "beginner",
            "duration_hours": 20.0,
            "tags": ["IoT", "Automatización", "Sensores", "Industria 4.0", "Hardware"],
            "career_hints": ["industrial", "sistemas"],
        },
        {
            "id": "cisco-data-analytics-essentials",
            "title": "Fundamentos de Analítica de Datos (Data Analytics)",
            "url": "https://skillsforall.com/course/data-analytics-essentials?courseLang=es-XL",
            "description": "Ciclo de vida del análisis de datos: recolección, transformación, visualización con hojas de cálculo y SQL para optimización de operaciones.",
            "level": "beginner",
            "duration_hours": 30.0,
            "tags": ["Data Analytics", "SQL", "Métricas", "Visualización"],
            "career_hints": ["industrial", "sistemas", "ia"],
        },
        {
            "id": "cisco-cloud-security",
            "title": "Seguridad en la Nube (Cloud Security)",
            "url": "https://skillsforall.com/course/cloud-security?courseLang=es-XL",
            "description": "Modelos de responsabilidad compartida, gestión de identidades y accesos (IAM), cifrado de datos en reposo y en tránsito en arquitecturas multinube.",
            "level": "intermediate",
            "duration_hours": 20.0,
            "tags": ["Cloud Security", "IAM", "Cifrado", "Multinube", "DevSecOps"],
            "career_hints": ["sistemas", "software"],
        },
        {
            "id": "cisco-green-it",
            "title": "Sostenibilidad de TI y Centros de Datos Verdes",
            "url": "https://skillsforall.com/course/engaging-in-green-it?courseLang=es-XL",
            "description": "Estrategias de eficiencia energética, reducción de huella de carbono en data centers y gestión sostenible del ciclo de vida del hardware.",
            "level": "beginner",
            "duration_hours": 10.0,
            "tags": ["Green IT", "Eficiencia Energética", "Sostenibilidad", "Data Centers"],
            "career_hints": ["industrial", "sistemas"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando catálogo oficial de 'Potencia tu Talento Digital' (PCM / Cisco)...")

        items = self.CATALOG
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"pcm-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://www.gob.pe/themes/custom/gobpe_theme/logo.svg",
                    language="es",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=item["duration_hours"],
                    instructor_name="Presidencia del Consejo de Ministros (PCM) & Cisco Networking Academy",
                    category_hint="Redes & Seguridad Informática",
                    tags=item["tags"],
                    provider_name="PCM / Cisco Skills for All",
                    credential_type="certificate",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=item.get("career_hints", ["sistemas"])
                )
            )

        logger.info("Talento Digital PCM: %d cursos procesados con éxito", len(courses))
        return courses
