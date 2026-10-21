import sys
from django.core.management.base import BaseCommand
from courses.ingestion.connectors import (
    AVAILABLE_CONNECTORS,
    get_connectors_by_group,
    get_connectors_by_tier,
)
from courses.ingestion.engine import CourseIngestionEngine

class Command(BaseCommand):
    help = "Sincroniza e ingesta cursos gratuitos desde plataformas externas hacia la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="all",
            help="Plataforma de origen a sincronizar (ej: microsoft_learn, kaggle, etc., o 'all'). Default: all",
        )
        parser.add_argument(
            "--group",
            type=str,
            default=None,
            help="Grupo de conectores a ejecutar (ej: ai, cloud, industrial, software, peru, code, university).",
        )
        parser.add_argument(
            "--tier",
            type=int,
            default=None,
            help="Ejecuta conectores hasta cierto tier de criticidad (1=Crítico/Rápido, 2=Institucional, 3=Secundario).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Límite máximo de cursos a procesar por conector (útil para pruebas y desarrollo).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Ejecuta la sincronización en modo de simulación sin modificar la base de datos.",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="Muestra la lista de conectores disponibles con su grupo y tier.",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self.stdout.write(self.style.NOTICE("\nCONECTORES DISPONIBLES EN EL SISTEMA:"))
            self.stdout.write(f"{'ID':<22} | {'TIER':<5} | {'GRUPO':<12} | {'NOMBRE':<35}")
            self.stdout.write("-" * 80)
            for cid, cls in sorted(AVAILABLE_CONNECTORS.items()):
                self.stdout.write(f"{cid:<22} | {cls.tier:<5} | {cls.group:<12} | {cls.platform_name:<35}")
            return

        source = options["source"].lower().strip()
        group = options["group"].lower().strip() if options["group"] else None
        tier = options["tier"]
        limit = options["limit"]
        dry_run = options["dry_run"]

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("INICIANDO SINCRONIZACIÓN DE CURSOS GRATUITOS"))
        self.stdout.write(f"Source: {source} | Group: {group or 'Todos'} | Tier: {tier or 'Todos'} | Límite: {limit or 'Sin límite'} | Dry-Run: {dry_run}")
        self.stdout.write(self.style.NOTICE("=" * 60))

        connectors_to_run = []
        if group:
            matched = get_connectors_by_group(group)
            if not matched:
                self.stdout.write(self.style.ERROR(f"No se encontraron conectores para el grupo '{group}'."))
                sys.exit(1)
            connectors_to_run = [c() for c in matched]
        elif tier:
            matched = get_connectors_by_tier(tier)
            connectors_to_run = [c() for c in matched]
        elif source == "all":
            connectors_to_run = [cls() for cls in AVAILABLE_CONNECTORS.values()]
        elif source in AVAILABLE_CONNECTORS:
            connectors_to_run = [AVAILABLE_CONNECTORS[source]()]
        else:
            self.stdout.write(self.style.ERROR(
                f"Plataforma '{source}' desconocida. Opciones disponibles: {list(AVAILABLE_CONNECTORS.keys()) + ['all']}"
            ))
            sys.exit(1)

        engine = CourseIngestionEngine(dry_run=dry_run)
        total_created = 0
        total_updated = 0
        total_unchanged = 0
        total_errors = 0

        for connector in connectors_to_run:
            self.stdout.write(f"\n>> Procesando conector: {connector.platform_name} ({connector.platform_id}) [Grupo: {connector.group}]...")
            stats = engine.process_connector(connector, limit=limit)

            self.stdout.write(self.style.SUCCESS(
                f"  [OK] Obtenidos: {stats['fetched']} | Creados: {stats['created']} | "
                f"Actualizados: {stats['updated']} | Sin cambios: {stats['unchanged']} | "
                f"Errores: {stats['errors']}"
            ))

            total_created += stats["created"]
            total_updated += stats["updated"]
            total_unchanged += stats["unchanged"]
            total_errors += stats["errors"]

        self.stdout.write("\n" + self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("RESUMEN GENERAL DE SINCRONIZACIÓN:"))
        self.stdout.write(self.style.SUCCESS(f"  Total Creados:      {total_created}"))
        self.stdout.write(self.style.WARNING(f"  Total Actualizados: {total_updated}"))
        self.stdout.write(f"  Total Sin Cambios:  {total_unchanged}")
        if total_errors > 0:
            self.stdout.write(self.style.ERROR(f"  Total con Errores:  {total_errors}"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if total_errors > 0 and total_created == 0 and total_updated == 0 and total_unchanged == 0:
            sys.exit(1)
