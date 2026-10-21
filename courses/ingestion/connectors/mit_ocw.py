import logging
from typing import List, Optional
import requests
from ..base import BaseCourseConnector, RawCourse
from ..normalizer import clean_text, normalize_level

logger = logging.getLogger(__name__)

# Nuevo endpoint oficial de la plataforma unificada Learn with MIT (https://learn.mit.edu/)
MIT_LEARN_API_URL = "https://api.learn.mit.edu/api/v1/learning_resources_search/"

class MitOcwConnector(BaseCourseConnector):
    platform_id = "mit_ocw"
    platform_name = "Learn with MIT | MIT Learn"

    def fetch_courses(self, limit: Optional[int] = 30) -> List[RawCourse]:
        fetch_size = limit if limit and limit <= 100 else 30
        logger.info("Consultando cursos gratuitos en la API de Learn with MIT (learn.mit.edu)...")

        params = {
            "free": "true",
            "resource_type": "course",
            "limit": fetch_size,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "UNI-OpenSource-Scraper/1.0"
        }

        try:
            response = requests.get(
                MIT_LEARN_API_URL,
                params=params,
                headers=headers,
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error("Error al conectar con la API de Learn with MIT: %s", e)
            return []

        results = data.get("results", [])
        raw_courses: List[RawCourse] = []

        for item in results:
            # 1. Filtro estricto: Solo cursos 100% gratuitos
            if not item.get("free", False):
                continue

            prices = item.get("prices") or []
            has_positive_price = False
            for p in prices:
                try:
                    price_val = float(str(p).replace("$", "").strip())
                    if price_val > 0.0:
                        has_positive_price = True
                        break
                except (ValueError, TypeError):
                    pass

            if has_positive_price:
                # Se descartan cursos con planes de pago o costos por certificado
                continue

            external_id = str(item.get("id") or item.get("readable_id") or "").strip()
            title = clean_text(item.get("title", ""))
            if not external_id or not title:
                continue

            # 2. URL oficial del curso apuntando a Learn with MIT (https://learn.mit.edu/)
            learn_url = item.get("learn_url")
            if not learn_url or not learn_url.startswith("http"):
                course_id = item.get("id")
                learn_url = f"https://learn.mit.edu/search?resource={course_id}" if course_id else (item.get("url") or "https://learn.mit.edu/")

            # 3. Imagen de portada del curso
            img_data = item.get("image")
            image_url = None
            if isinstance(img_data, dict):
                image_url = img_data.get("url")
            elif isinstance(img_data, str) and img_data.startswith("http"):
                image_url = img_data

            # 4. Datos de la primera sesión / run disponible
            runs = item.get("runs", [])
            run_data = runs[0] if runs else {}

            instructors = run_data.get("instructors", [])
            instructor_names = [
                i.get("full_name") for i in instructors
                if isinstance(i, dict) and i.get("full_name")
            ]
            instructor_str = ", ".join(instructor_names)[:140] if instructor_names else "MIT Faculty"

            # Nivel
            raw_levels = run_data.get("level", [])
            level_name = ""
            if raw_levels and isinstance(raw_levels[0], dict):
                level_name = raw_levels[0].get("name", "")
            elif raw_levels and isinstance(raw_levels[0], str):
                level_name = raw_levels[0]
            normalized_level = normalize_level(level_name)

            # Temas y tags
            topic_objects = item.get("topics", [])
            topics = [
                clean_text(t.get("name", "")) for t in topic_objects
                if isinstance(t, dict) and clean_text(t.get("name", ""))
            ]
            tags = list(topics)
            tags.append("mit")
            tags.append("mit-learn")

            # Descripción
            short_desc = clean_text(item.get("description") or run_data.get("short_description") or "")
            if len(short_desc) > 250:
                short_desc = short_desc[:247] + "..."

            full_desc = (
                f"Curso gratuito ofrecido a través de Learn with MIT (https://learn.mit.edu/). "
                f"Impartido por {instructor_str}. Incluye materiales académicos abiertos, "
                "lecciones y recursos interactivos de aprendizaje."
            )

            # Duración estimada
            duration_str = run_data.get("duration") or item.get("duration") or ""
            duration_hours = 40.0
            if "week" in str(duration_str).lower():
                try:
                    num_weeks = int("".join(filter(str.isdigit, str(duration_str)[:5])))
                    duration_hours = float(num_weeks * 5)
                except Exception:
                    duration_hours = 40.0

            has_cert = bool(item.get("certification", False))

            raw_course = RawCourse(
                platform=self.platform_id,
                external_id=external_id,
                title=f"{title} (MIT Learn)",
                url=learn_url,
                short_description=short_desc or f"Curso de {title} en Learn with MIT.",
                description=full_desc,
                image_url=image_url,
                level=normalized_level,
                resource_type="platform",
                has_certification=has_cert,
                language="en",
                duration_hours=duration_hours,
                instructor_name=instructor_str,
                category_hint=" ".join(topics),
                tags=tags
            )
            raw_courses.append(raw_course)

            if limit and len(raw_courses) >= limit:
                break

        logger.info("Learn with MIT: %d cursos gratuitos procesados exitosamente.", len(raw_courses))
        return raw_courses
