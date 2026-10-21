import re
from typing import List, Set
from courses.models import Career
from .base import RawJob

INDUSTRIAL_KEYWORDS = [
    "industrial", "procesos", "logistica", "logística", "supply chain", "cadena de suministro",
    "calidad", "operaciones", "planner", "planeamiento", "lean", "six sigma", "mejora continua",
    "planta", "inventario", "almacen", "almacén", "seguridad industrial", "produccion", "producción",
    "comercial", "compras", "proyectos industriales", "gestion de procesos", "gestión de procesos"
]

SYSTEMS_KEYWORDS = [
    "sistemas", "redes", "ciberseguridad", "cybersecurity", "seguridad de la informacion",
    "infraestructura", "cloud", "aws", "azure", "gcp", "devops", "sysadmin", "administrador de sistemas",
    "arquitectura de sistemas", "base de datos", "dba", "soporte ti", "telecomunicaciones", "networking",
    "linux", "seguridad perimetral", "datacenter", "centro de datos"
]

SOFTWARE_KEYWORDS = [
    "software", "desarrollador", "developer", "backend", "frontend", "full stack", "fullstack",
    "programador", "programacion", "programación", "python", "react", "javascript", "typescript",
    "nodejs", "node.js", "django", "fastapi", "java", "spring", "c#", ".net", "dotnet", "golang",
    "mobile", "android", "ios", "flutter", "react native", "api", "rest", "microservicios", "git"
]

AI_KEYWORDS = [
    "inteligencia artificial", "artificial intelligence", "machine learning", "deep learning", "ai",
    "data scientist", "cientifico de datos", "científico de datos", "data analyst", "analista de datos",
    "mlops", "nlp", "procesamiento de lenguaje natural", "computer vision", "vision por computadora",
    "llm", "generative ai", "ia generativa", "big data", "spark", "hadoop", "tensorflow", "pytorch",
    "power bi", "looker", "tableau", "bi", "business intelligence", "sql analitico"
]

class JobCareerClassifier:
    """
    Clasificador inteligente de vacantes laborales para asignarlas a las 4 carreras
    de ingeniería de la UNI según el título, descripción y requisitos técnicos.
    """

    @classmethod
    def classify(cls, raw: RawJob) -> List[Career]:
        assigned_codes: Set[str] = set()

        # 1. Considerar hints explícitos proporcionados por el conector
        if raw.career_hints:
            for hint in raw.career_hints:
                assigned_codes.add(hint.lower().strip())

        # 2. Análisis heurístico del texto completo
        text_corpus = f"{raw.title} {raw.short_description} {raw.description} {raw.requirements_summary} {' '.join(raw.tags)}".lower()
        # Normalizar tildes para búsqueda flexible
        clean_corpus = (
            text_corpus.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        for kw in INDUSTRIAL_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_corpus):
                assigned_codes.add(Career.INDUSTRIAL)
                break

        for kw in SYSTEMS_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_corpus):
                assigned_codes.add(Career.SYSTEMS)
                break

        for kw in SOFTWARE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_corpus):
                assigned_codes.add(Career.SOFTWARE)
                break

        for kw in AI_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_corpus):
                assigned_codes.add(Career.AI)
                break

        # Fallback a software/sistemas si no hubo coincidencia específica
        if not assigned_codes:
            assigned_codes.add(Career.SOFTWARE)
            assigned_codes.add(Career.SYSTEMS)

        # Retornar los objetos Career correspondientes
        return list(Career.objects.filter(code__in=assigned_codes))
