import logging
import urllib.request
import json
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class MicrosoftLearnConnector(BaseCourseConnector):
    """
    Conector oficial para Microsoft Learn vía Catalog API (es-es).
    Ingesta rutas de aprendizaje (learningPaths) y módulos oficiales gratuitos
    cubriendo Ingeniería de Software, Sistemas, IA y Power Platform.
    """
    platform_id = "microsoft_learn"
    platform_name = "Microsoft Learn"
    tier = 1
    group = "cloud"

    CATALOG_API_URL = "https://learn.microsoft.com/api/catalog/?locale=es-es"

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Consultando API de Microsoft Learn Catalog...")

        req = urllib.request.Request(
            self.CATALOG_API_URL,
            headers={
                "User-Agent": "UNI-OpenSource-Bot/1.0 (+https://github.com/uni-open-source)",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error("Error al obtener catálogo de Microsoft Learn: %s", e)
            return courses

        learning_paths = data.get("learningPaths", [])
        modules = data.get("modules", [])
        logger.info("Recibidos %d learningPaths y %d modules de Microsoft Learn", len(learning_paths), len(modules))

        # Priorizar Learning Paths ya que agrupan módulos con insignias de finalización
        for lp in learning_paths:
            if limit and len(courses) >= limit:
                break

            uid = lp.get("uid")
            title = lp.get("title")
            summary = lp.get("summary") or ""
            url = lp.get("url")
            if not uid or not title or not url:
                continue

            duration_min = lp.get("duration_in_minutes") or 0
            duration_hours = round(duration_min / 60.0, 2) if duration_min else None

            # Nivel
            raw_levels = lp.get("levels", [])
            level = "beginner"
            if "advanced" in raw_levels:
                level = "advanced"
            elif "intermediate" in raw_levels:
                level = "intermediate"

            # Tags
            roles = lp.get("roles", [])
            products = lp.get("products", [])
            subjects = lp.get("subjects", [])
            tags = list(set([r for r in roles + products + subjects if isinstance(r, str)]))[:6]

            # Hints de carrera
            career_hints = []
            combined_text = f"{title} {summary} {' '.join(tags)}".lower()
            if any(k in combined_text for k in ["machine-learning", "ai", "inteligencia artificial", "vision", "openai", "copilot", "data-scientist"]):
                career_hints.append("ia")
            if any(k in combined_text for k in ["azure", "cloud", "devops", "security", "seguridad", "administrator", "redes", "infrastructure"]):
                career_hints.append("sistemas")
            if any(k in combined_text for k in ["developer", "dotnet", ".net", "c#", "python", "javascript", "api", "software", "github"]):
                career_hints.append("software")
            if any(k in combined_text for k in ["power-bi", "power-apps", "power-automate", "business-analyst", "procesos"]):
                career_hints.append("industrial")

            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"path-{uid}",
                    title=title,
                    description=summary,
                    short_description=summary[:250],
                    url=url,
                    image_url=lp.get("icon_url"),
                    language="es",
                    level=level,
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=duration_hours,
                    instructor_name="Microsoft Learn",
                    category_hint="Cloud Computing & DevOps",
                    tags=tags,
                    provider_name="Microsoft",
                    credential_type="skill_badge",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=career_hints
                )
            )

        # Si aún no llegamos al límite y hay cupo, tomar módulos destacados
        if not limit or len(courses) < limit:
            for mod in modules:
                if limit and len(courses) >= limit:
                    break

                uid = mod.get("uid")
                title = mod.get("title")
                summary = mod.get("summary") or ""
                url = mod.get("url")
                if not uid or not title or not url:
                    continue

                duration_min = mod.get("duration_in_minutes") or 0
                duration_hours = round(duration_min / 60.0, 2) if duration_min else None

                raw_levels = mod.get("levels", [])
                level = "beginner"
                if "advanced" in raw_levels:
                    level = "advanced"
                elif "intermediate" in raw_levels:
                    level = "intermediate"

                roles = mod.get("roles", [])
                products = mod.get("products", [])
                subjects = mod.get("subjects", [])
                tags = list(set([r for r in roles + products + subjects if isinstance(r, str)]))[:5]

                courses.append(
                    RawCourse(
                        platform=self.platform_id,
                        external_id=f"module-{uid}",
                        title=title,
                        description=summary,
                        short_description=summary[:250],
                        url=url,
                        image_url=mod.get("icon_url"),
                        language="es",
                        level=level,
                        resource_type="interactive",
                        has_certification=True,
                        duration_hours=duration_hours,
                        instructor_name="Microsoft Learn",
                        category_hint="Cloud Computing & DevOps",
                        tags=tags,
                        provider_name="Microsoft",
                        credential_type="skill_badge",
                        is_free_credential=True,
                        has_practical_labs=True,
                        career_hints=[]
                    )
                )

        logger.info("Microsoft Learn: Ingestados %d cursos listos para persistir", len(courses))
        return courses
