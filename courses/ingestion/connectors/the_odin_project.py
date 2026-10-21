import logging
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class TheOdinProjectConnector(BaseCourseConnector):
    """
    Conector para The Odin Project (https://www.theodinproject.com/).
    Currículum open-source de excelencia para Ingeniería de Software Full-Stack.
    Cursos 100% gratuitos basados en proyectos y repositorios de GitHub.
    Tipo de credencial: sin certificado formal ('none'), enfocado en portfolio verificable.
    """
    platform_id = "the_odin_project"
    platform_name = "The Odin Project"
    tier = 1
    group = "software"

    PATHS = [
        {
            "id": "foundations",
            "title": "Foundations of Web Development",
            "url": "https://www.theodinproject.com/paths/foundations/courses/foundations",
            "description": "Fundamentos indispensables para ingenieros de software: Git y GitHub, flujo de trabajo en terminal Linux/Unix, HTML5 semántico, CSS3 moderno (Flexbox) y lógica básica de JavaScript.",
            "level": "beginner",
            "duration_hours": 40.0,
            "tags": ["Git", "GitHub", "HTML5", "CSS3", "JavaScript", "Terminal", "Linux"],
            "career_hints": ["software", "sistemas"],
        },
        {
            "id": "full-stack-javascript",
            "title": "Full Stack JavaScript Path",
            "url": "https://www.theodinproject.com/paths/full-stack-javascript",
            "description": "Ruta completa de desarrollo full-stack: JavaScript avanzado (POO, diseño modular, APIs), React, NodeJS, Express, bases de datos PostgreSQL/Prisma, autenticación JWT y testing automatizado.",
            "level": "intermediate",
            "duration_hours": 120.0,
            "tags": ["JavaScript", "React", "NodeJS", "Express", "PostgreSQL", "APIs", "Full Stack"],
            "career_hints": ["software"],
        },
        {
            "id": "full-stack-ruby",
            "title": "Full Stack Ruby on Rails Path",
            "url": "https://www.theodinproject.com/paths/full-stack-ruby-on-rails",
            "description": "Desarrollo backend y arquitecturas web robustas con Ruby y Rails: principios SOLID, diseño MVC, Active Record, migraciones, pruebas con RSpec y despliegue continuo.",
            "level": "intermediate",
            "duration_hours": 110.0,
            "tags": ["Ruby", "Ruby on Rails", "MVC", "PostgreSQL", "RSpec", "Backend", "SOLID"],
            "career_hints": ["software"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando rutas oficiales de The Odin Project...")

        items = self.PATHS
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"top-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://www.theodinproject.com/assets/badge-foundations-77a33a3c.svg",
                    language="en",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=False,
                    duration_hours=item["duration_hours"],
                    instructor_name="The Odin Project Community",
                    category_hint="Desarrollo Web & Frontend",
                    tags=item["tags"],
                    provider_name="The Odin Project",
                    credential_type="none",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=item.get("career_hints", ["software"])
                )
            )

        logger.info("The Odin Project: %d rutas procesadas con éxito", len(courses))
        return courses
