import logging
import time
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone

from courses.models import Course, SyncAuditLog
from .base import BaseCourseConnector, RawCourse
from .classifier import CareerClassifier
from .hasher import compute_course_hash
from .normalizer import generate_safe_slug, clean_text, strip_emojis
from .taxonomy import TaxonomyResolver

logger = logging.getLogger(__name__)

class CourseIngestionEngine:
    """
    Motor de sincronización e ingesta idempotente para cursos.
    Realiza detección de cambios mediante SHA-256 e inserción / actualización atómica,
    con clasificación multi carrera, auditoría centralizada y sanitización sin emojis.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def process_connector(self, connector: BaseCourseConnector, limit: Optional[int] = None) -> Dict[str, int]:
        stats = {
            "platform": connector.platform_id,
            "fetched": 0,
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0,
        }
        start_time = time.time()

        logger.info("Iniciando ingesta para [%s] (dry_run=%s)", connector.platform_name, self.dry_run)
        raw_courses: List[RawCourse] = []
        critical_error_msg = ""
        try:
            raw_courses = connector.fetch_courses(limit=limit)
            stats["fetched"] = len(raw_courses)
        except Exception as e:
            logger.error("Fallo crítico en conector [%s]: %s", connector.platform_id, e)
            critical_error_msg = str(e)
            stats["errors"] += 1

        for raw in raw_courses:
            try:
                res = self.upsert_course(raw)
                if res in stats:
                    stats[res] += 1
            except Exception as e:
                logger.error("Error al procesar curso [%s:%s]: %s", raw.platform, raw.external_id, e)
                stats["errors"] += 1

        duration_seconds = round(time.time() - start_time, 2)
        logger.info("Resumen para [%s] en %.2fs: %s", connector.platform_id, duration_seconds, stats)

        if not self.dry_run:
            if stats["errors"] == 0:
                audit_status = SyncAuditLog.STATUS_SUCCESS
            elif stats["created"] > 0 or stats["updated"] > 0 or stats["unchanged"] > 0:
                audit_status = SyncAuditLog.STATUS_WARNING
            else:
                audit_status = SyncAuditLog.STATUS_ERROR

            details_text = (
                f"Sincronización finalizada en {duration_seconds}s. "
                f"Creados: {stats['created']}, Actualizados: {stats['updated']}, "
                f"Sin cambios: {stats['unchanged']}, Errores: {stats['errors']}."
            )
            if critical_error_msg:
                details_text += f"\nError crítico: {critical_error_msg}"

            try:
                SyncAuditLog.objects.create(
                    platform=connector.platform_id,
                    status=audit_status,
                    courses_fetched=stats["fetched"],
                    courses_created=stats["created"],
                    courses_updated=stats["updated"],
                    courses_unchanged=stats["unchanged"],
                    errors_count=stats["errors"],
                    duration_seconds=duration_seconds,
                    details=details_text
                )
            except Exception as e:
                logger.error("Error al registrar auditoría en SyncAuditLog: %s", e)

        return stats

    def upsert_course(self, raw: RawCourse) -> str:
        """
        Inserta o actualiza un curso de acuerdo a su hash, sanitizando emojis.
        Retorna: 'created', 'updated' o 'unchanged'.
        """
        now = timezone.now()

        # Sanitización de emojis y normalización textual
        clean_title = strip_emojis(raw.title)[:120].strip()
        clean_desc = clean_text(raw.description)
        clean_short = strip_emojis(raw.short_description or clean_desc[:250])[:255].strip()
        clean_provider = strip_emojis(raw.provider_name or "")[:100].strip()
        clean_instructor = strip_emojis(raw.instructor_name or "")[:150].strip()
        if raw.tags:
            raw.tags = [strip_emojis(t) for t in raw.tags if strip_emojis(t)]

        # Preparar diccionario para cálculo de hash
        course_data = {
            "title": clean_title,
            "description": clean_desc,
            "short_description": clean_short,
            "url": raw.url[:500],
            "level": raw.level,
            "resource_type": raw.resource_type,
            "has_certification": raw.has_certification,
            "language": raw.language,
            "duration_hours": raw.duration_hours,
            "instructor_name": clean_instructor,
            "external_image_url": raw.image_url[:500] if raw.image_url else None,
            "provider_name": clean_provider,
            "credential_type": raw.credential_type,
            "is_free_credential": raw.is_free_credential,
            "has_practical_labs": raw.has_practical_labs,
        }
        new_hash = compute_course_hash(course_data)

        # Buscar si ya existe por llave compuesta (platform, external_id)
        existing_course = Course.objects.filter(
            platform=raw.platform,
            external_id=raw.external_id
        ).first()

        if existing_course:
            # Caso 1: El curso no ha sufrido modificaciones
            if existing_course.content_hash == new_hash:
                if not self.dry_run:
                    existing_course.last_synced_at = now
                    existing_course.sync_status = "active"
                    existing_course.save(update_fields=["last_synced_at", "sync_status"])
                return "unchanged"

            # Caso 2: El contenido cambió en la fuente externa
            if not self.dry_run:
                with transaction.atomic():
                    for attr, val in course_data.items():
                        setattr(existing_course, attr, val)
                    existing_course.content_hash = new_hash
                    existing_course.last_synced_at = now
                    existing_course.sync_status = "active"
                    existing_course.save()

                    # Actualizar tags y carreras
                    if raw.tags:
                        tag_objs = TaxonomyResolver.resolve_tags(raw.tags)
                        existing_course.tags.set(tag_objs)
                    career_objs = CareerClassifier.classify(raw)
                    if career_objs:
                        existing_course.careers.set(career_objs)
            return "updated"

        # Caso 3: Es un curso nuevo
        if self.dry_run:
            return "created"

        with transaction.atomic():
            # Generar slug único
            base_slug = generate_safe_slug(raw.title, raw.external_id)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug[:135]}-{counter}"
                counter += 1

            # Resolver categoría
            category = TaxonomyResolver.resolve_category(
                title=raw.title,
                category_hint=raw.category_hint,
                tags=raw.tags
            )

            new_course = Course(
                title=course_data["title"],
                slug=slug,
                short_description=course_data["short_description"],
                description=course_data["description"],
                url=course_data["url"],
                category=category,
                level=course_data["level"],
                resource_type=course_data["resource_type"],
                has_certification=course_data["has_certification"],
                language=course_data["language"],
                duration_hours=course_data["duration_hours"],
                instructor_name=course_data["instructor_name"],
                external_image_url=course_data["external_image_url"],
                provider_name=course_data["provider_name"],
                credential_type=course_data["credential_type"],
                is_free_credential=course_data["is_free_credential"],
                has_practical_labs=course_data["has_practical_labs"],
                platform=raw.platform,
                external_id=raw.external_id,
                content_hash=new_hash,
                last_synced_at=now,
                sync_status="active",
                is_published=True,
                owner=None
            )
            new_course.save()

            if raw.tags:
                tag_objs = TaxonomyResolver.resolve_tags(raw.tags)
                new_course.tags.set(tag_objs)

            career_objs = CareerClassifier.classify(raw)
            if career_objs:
                new_course.careers.set(career_objs)

        return "created"
