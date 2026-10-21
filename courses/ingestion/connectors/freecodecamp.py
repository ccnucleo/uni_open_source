import logging
from typing import List, Optional
import requests
from ..base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://curriculum-db.freecodecamp.org/graphql"

class FreeCodeCampConnector(BaseCourseConnector):
    platform_id = "freecodecamp"
    platform_name = "freeCodeCamp"

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        query = """
        query {
            superblocks {
                name
                dashedName
                isCertification
            }
        }
        """
        logger.info("Consultando catálogo GraphQL de freeCodeCamp...")
        try:
            response = requests.post(
                GRAPHQL_URL,
                json={"query": query},
                headers={"Content-Type": "application/json", "User-Agent": "UNI-OpenSource-Scraper/1.0"},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error("Error al conectar con la API de freeCodeCamp: %s", e)
            return []

        superblocks = data.get("data", {}).get("superblocks", [])
        raw_courses: List[RawCourse] = []

        # Filtrar o excluir playgrounds internos no orientados a aprendizaje
        excluded_slugs = {"dev-playground", "rosetta-code"}

        for item in superblocks:
            dashed_name = item.get("dashedName", "").strip()
            name = item.get("name", "").strip()
            if not dashed_name or dashed_name in excluded_slugs:
                continue

            # Generar tags a partir del nombre y slug
            tag_tokens = [t for t in dashed_name.split("-") if len(t) > 2 and not t.isdigit()]
            tag_tokens.append("freecodecamp")

            # Determinar idioma aproximado
            language = "es" if "spanish" in dashed_name else "en"

            # Duración estimada: Las certificaciones de freeCodeCamp se calculan en ~300 horas
            is_cert = bool(item.get("isCertification", False))
            duration = 300.0 if is_cert else 40.0

            course_url = f"https://www.freecodecamp.org/learn/{dashed_name}/"
            if language == "es":
                course_url = f"https://www.freecodecamp.org/espanol/learn/{dashed_name}/"

            raw_course = RawCourse(
                platform=self.platform_id,
                external_id=dashed_name,
                title=f"{name} (freeCodeCamp)",
                url=course_url,
                short_description=f"Ruta de aprendizaje y certificación interactiva de {name} en freeCodeCamp.",
                description=(
                    f"Aprende {name} paso a paso con el currículo oficial y abierto de freeCodeCamp. "
                    "Incluye proyectos prácticos interactivos, retos de programación y opción de certificación gratuita."
                ),
                image_url="https://design-style-guide.freecodecamp.org/downloads/fcc_primary_large.png",
                level="beginner",
                resource_type="platform",
                has_certification=is_cert,
                language=language,
                duration_hours=duration,
                instructor_name="freeCodeCamp Community",
                category_hint=name,
                tags=tag_tokens
            )
            raw_courses.append(raw_course)

            if limit and len(raw_courses) >= limit:
                break

        logger.info("freeCodeCamp: %d cursos procesados exitosamente.", len(raw_courses))
        return raw_courses
