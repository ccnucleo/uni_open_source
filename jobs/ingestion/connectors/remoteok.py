import datetime
import json
import logging
import urllib.request
from typing import List, Optional
from jobs.ingestion.base import BaseJobConnector, RawJob
from courses.ingestion.normalizer import strip_emojis, clean_text

logger = logging.getLogger(__name__)

class RemoteOkConnector(BaseJobConnector):
    """
    Conector oficial para RemoteOK (https://remoteok.com/).
    Extrae ofertas remotas internacionales en desarrollo de software, IA, datos,
    DevOps y arquitectura de sistemas.
    """
    portal_id = "remoteok"
    portal_name = "RemoteOK (Tech Remoto)"
    group = "global"
    tier = 1

    ENDPOINT = "https://remoteok.com/api"

    def fetch_jobs(self, limit: Optional[int] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        logger.info("Consultando API oficial de RemoteOK...")

        req = urllib.request.Request(
            self.ENDPOINT,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.error("Error al obtener catálogo de RemoteOK: %s", e)
            return jobs

        # El primer elemento de RemoteOK suele ser metadata legal
        items = [x for x in data if isinstance(x, dict) and "position" in x]

        for item in items:
            if limit and len(jobs) >= limit:
                break

            job_id = item.get("id")
            title = item.get("position")
            url = item.get("url")
            company = item.get("company", "Empresa Global")

            if not job_id or not title or not url:
                continue

            raw_desc = item.get("description", "")
            tags = item.get("tags", [])
            location = item.get("location", "Remoto Mundial")

            # Salario
            min_sal = item.get("salary_min")
            max_sal = item.get("salary_max")
            has_sal = bool(min_sal or max_sal)

            # Fecha
            epoch = item.get("epoch")
            pub_dt = None
            if epoch:
                try:
                    pub_dt = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc)
                except Exception:
                    pass

            jobs.append(
                RawJob(
                    portal=self.portal_id,
                    external_id=str(job_id),
                    title=strip_emojis(title),
                    company_name=strip_emojis(company),
                    url=url,
                    company_logo_url=item.get("company_logo"),
                    country="Global",
                    city=strip_emojis(location)[:80],
                    modality="remoto",
                    contract_type="tiempo_completo",
                    seniority="senior" if "senior" in title.lower() else ("lead" if "lead" in title.lower() else "semi_senior"),
                    salary_currency="USD",
                    salary_min=float(min_sal) if min_sal else None,
                    salary_max=float(max_sal) if max_sal else None,
                    salary_visible=has_sal,
                    description=clean_text(raw_desc),
                    short_description=clean_text(raw_desc)[:280],
                    requirements_summary="",
                    tags=[strip_emojis(t) for t in tags if isinstance(t, str)][:8],
                    published_at=pub_dt,
                )
            )

        logger.info("RemoteOK: %d vacantes recopiladas con éxito", len(jobs))
        return jobs
