import datetime
import json
import logging
import urllib.request
from typing import List, Optional
from jobs.ingestion.base import BaseJobConnector, RawJob
from courses.ingestion.normalizer import strip_emojis, clean_text

logger = logging.getLogger(__name__)

class GetOnBrdConnector(BaseJobConnector):
    """
    Conector oficial para Get on Board (https://www.getonbrd.com/).
    Extrae ofertas técnicas de desarrollo de software, ciencia de datos, IA y ciberseguridad
    en Latinoamérica y con modalidades remotas/híbridas.
    """
    portal_id = "getonbrd"
    portal_name = "Get on Board (Tech LatAm)"
    group = "latam"
    tier = 1

    ENDPOINTS = [
        "https://www.getonbrd.com/api/v0/categories/programming/jobs?per_page=25",
        "https://www.getonbrd.com/api/v0/categories/data-science-analytics/jobs?per_page=25",
        "https://www.getonbrd.com/api/v0/categories/sysadmin-devops-qa/jobs?per_page=25",
    ]

    def fetch_jobs(self, limit: Optional[int] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        logger.info("Consultando API de Get on Board...")

        for endpoint in self.ENDPOINTS:
            if limit and len(jobs) >= limit:
                break

            req = urllib.request.Request(
                endpoint,
                headers={"User-Agent": "UNI-OpenSource-JobsBot/1.0 (+https://github.com/uni-open-source)"}
            )

            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                logger.error("Error al consultar Get on Board [%s]: %s", endpoint, e)
                continue

            data_items = payload.get("data", [])
            for item in data_items:
                if limit and len(jobs) >= limit:
                    break

                job_id = item.get("id")
                attrs = item.get("attributes", {})
                links = item.get("links", {})
                title = attrs.get("title")
                url = links.get("public_url")

                if not job_id or not title or not url:
                    continue

                # Modalidad
                is_remote = attrs.get("remote", False)
                remote_mod = attrs.get("remote_modality", "")
                if is_remote:
                    modality = "remoto"
                elif "hybrid" in remote_mod.lower():
                    modality = "hibrido"
                else:
                    modality = "presencial"

                countries = attrs.get("countries", [])
                country = countries[0] if countries else "PE"

                # Salario
                min_sal = attrs.get("min_salary")
                max_sal = attrs.get("max_salary")
                has_sal = bool(min_sal or max_sal)

                # Publicación
                pub_ts = attrs.get("published_at")
                pub_dt = None
                if pub_ts:
                    try:
                        pub_dt = datetime.datetime.fromtimestamp(pub_ts, tz=datetime.timezone.utc)
                    except Exception:
                        pass

                raw_desc = attrs.get("description", "")
                raw_functions = attrs.get("functions", "")
                raw_benefits = attrs.get("benefits", "")
                full_desc = f"{raw_desc}\n\n{raw_functions}\n\n{raw_benefits}".strip()

                jobs.append(
                    RawJob(
                        portal=self.portal_id,
                        external_id=str(job_id),
                        title=title,
                        company_name=strip_emojis(attrs.get("company_name", "Empresa Tecnológica")),
                        url=url,
                        company_logo_url=attrs.get("company_logo_url"),
                        country=country,
                        city="Lima" if "peru" in str(countries).lower() else "Remoto LatAm",
                        modality=modality,
                        contract_type="tiempo_completo",
                        seniority="junior" if "junior" in title.lower() else ("senior" if "senior" in title.lower() else "semi_senior"),
                        salary_currency="USD",
                        salary_min=float(min_sal) if min_sal else None,
                        salary_max=float(max_sal) if max_sal else None,
                        salary_visible=has_sal,
                        description=full_desc,
                        short_description=clean_text(raw_desc)[:280],
                        requirements_summary=clean_text(raw_functions)[:500],
                        tags=[attrs.get("category_name", "Tech")],
                        published_at=pub_dt,
                    )
                )

        logger.info("Get on Board: %d vacantes recopiladas con éxito", len(jobs))
        return jobs
