import logging
import time
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone

from courses.ingestion.normalizer import strip_emojis, clean_text
from courses.ingestion.taxonomy import TaxonomyResolver
from jobs.models import JobListing, JobSyncAuditLog
from .base import BaseJobConnector, RawJob
from .classifier import JobCareerClassifier
from .hasher import compute_job_hash
from .normalizer import (
    generate_safe_job_slug,
    normalize_modality,
    normalize_seniority,
    normalize_contract_type,
)

logger = logging.getLogger(__name__)

class JobIngestionEngine:
    """
    Motor centralizado de ingesta, deduplicación e idempotencia para vacantes laborales.
    Garantiza almacenamiento relacional en Supabase con hash determinista SHA-256,
    clasificación multi-carrera de ingeniería y trazabilidad en JobSyncAuditLog.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def process_connector(self, connector: BaseJobConnector, limit: Optional[int] = None) -> Dict[str, int]:
        stats = {
            "portal": connector.portal_id,
            "fetched": 0,
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0,
        }
        start_time = time.time()
        logger.info("Iniciando recopilación de empleos en [%s] (dry_run=%s)", connector.portal_name, self.dry_run)

        raw_jobs: List[RawJob] = []
        critical_error = ""
        try:
            raw_jobs = connector.fetch_jobs(limit=limit)
            stats["fetched"] = len(raw_jobs)
        except Exception as e:
            logger.error("Error crítico en conector de empleos [%s]: %s", connector.portal_id, e)
            critical_error = str(e)
            stats["errors"] += 1

        for raw in raw_jobs:
            try:
                res = self.upsert_job(raw)
                if res in stats:
                    stats[res] += 1
            except Exception as e:
                logger.error("Error al procesar vacante [%s:%s]: %s", raw.portal, raw.external_id, e)
                stats["errors"] += 1

        duration_seconds = round(time.time() - start_time, 2)
        logger.info("Fin de ingesta para [%s] en %.2fs: %s", connector.portal_id, duration_seconds, stats)

        if not self.dry_run:
            if stats["errors"] == 0:
                audit_status = JobSyncAuditLog.STATUS_SUCCESS
            elif (stats["created"] + stats["updated"] + stats["unchanged"]) > 0:
                audit_status = JobSyncAuditLog.STATUS_WARNING
            else:
                audit_status = JobSyncAuditLog.STATUS_ERROR

            details = (
                f"Sincronización finalizada en {duration_seconds}s. "
                f"Creadas: {stats['created']}, Actualizadas: {stats['updated']}, "
                f"Sin cambios: {stats['unchanged']}, Errores: {stats['errors']}."
            )
            if critical_error:
                details += f"\nFallo crítico: {critical_error}"

            try:
                JobSyncAuditLog.objects.create(
                    portal=connector.portal_id,
                    status=audit_status,
                    jobs_fetched=stats["fetched"],
                    jobs_created=stats["created"],
                    jobs_updated=stats["updated"],
                    jobs_unchanged=stats["unchanged"],
                    errors_count=stats["errors"],
                    duration_seconds=duration_seconds,
                    details=details,
                )
            except Exception as log_err:
                logger.error("No se pudo guardar JobSyncAuditLog: %s", log_err)

        return stats

    def upsert_job(self, raw: RawJob) -> str:
        now = timezone.now()

        # Sanitización de emojis y normalización de textos
        clean_title = strip_emojis(raw.title)[:200].strip()
        clean_company = strip_emojis(raw.company_name)[:150].strip()
        clean_desc = clean_text(raw.description)
        clean_short = strip_emojis(raw.short_description or clean_desc[:280])[:300].strip()
        clean_reqs = clean_text(raw.requirements_summary)
        clean_city = strip_emojis(raw.city or "Lima")[:100].strip()

        modality = normalize_modality(raw.modality)
        contract = normalize_contract_type(raw.contract_type)
        seniority = normalize_seniority(raw.seniority)

        job_data = {
            "title": clean_title,
            "company_name": clean_company,
            "url": raw.url[:500],
            "company_logo_url": raw.company_logo_url[:500] if raw.company_logo_url else None,
            "country": raw.country[:50] if raw.country else "PE",
            "city": clean_city,
            "modality": modality,
            "contract_type": contract,
            "seniority": seniority,
            "salary_currency": raw.salary_currency or "PEN",
            "salary_min": raw.salary_min,
            "salary_max": raw.salary_max,
            "salary_visible": raw.salary_visible,
            "description": clean_desc,
            "short_description": clean_short,
            "requirements_summary": clean_reqs,
            "published_at": raw.published_at or now,
            "last_verified_at": now,
            "status": "active",
        }

        new_hash = compute_job_hash(job_data)

        # Buscar si ya existe por llave compuesta (portal, external_id)
        existing = JobListing.objects.filter(portal=raw.portal, external_id=raw.external_id).first()

        if existing:
            # Caso 1: Sin modificaciones
            if existing.content_hash == new_hash:
                if not self.dry_run:
                    existing.last_verified_at = now
                    existing.status = "active"
                    existing.save(update_fields=["last_verified_at", "status"])
                return "unchanged"

            # Caso 2: Contenido actualizado en el portal
            if not self.dry_run:
                with transaction.atomic():
                    for attr, val in job_data.items():
                        setattr(existing, attr, val)
                    existing.content_hash = new_hash
                    existing.save()

                    # Actualizar tags y carreras
                    if raw.tags:
                        tags_objs = TaxonomyResolver.resolve_tags(raw.tags)
                        existing.tags.set(tags_objs)
                    career_objs = JobCareerClassifier.classify(raw)
                    if career_objs:
                        existing.careers.set(career_objs)
            return "updated"

        # Caso 3: Nueva vacante
        if self.dry_run:
            return "created"

        with transaction.atomic():
            base_slug = generate_safe_job_slug(clean_company, clean_title, raw.external_id)
            slug = base_slug
            counter = 1
            while JobListing.objects.filter(slug=slug).exists():
                slug = f"{base_slug[:200]}-{counter}"
                counter += 1

            new_job = JobListing(
                title=job_data["title"],
                slug=slug,
                company_name=job_data["company_name"],
                company_logo_url=job_data["company_logo_url"],
                portal=raw.portal,
                external_id=raw.external_id,
                url=job_data["url"],
                country=job_data["country"],
                city=job_data["city"],
                modality=job_data["modality"],
                contract_type=job_data["contract_type"],
                seniority=job_data["seniority"],
                salary_currency=job_data["salary_currency"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                salary_visible=job_data["salary_visible"],
                short_description=job_data["short_description"],
                description=job_data["description"],
                requirements_summary=job_data["requirements_summary"],
                published_at=job_data["published_at"],
                last_verified_at=job_data["last_verified_at"],
                status=job_data["status"],
                content_hash=new_hash,
            )
            new_job.save()

            if raw.tags:
                tags_objs = TaxonomyResolver.resolve_tags(raw.tags)
                new_job.tags.set(tags_objs)

            career_objs = JobCareerClassifier.classify(raw)
            if career_objs:
                new_job.careers.set(career_objs)

        return "created"
