from typing import List
from courses.models import Career

CAREER_KEYWORDS = {
    Career.INDUSTRIAL: [
        "logística", "logistica", "supply chain", "cadena de suministro",
        "procesos", "calidad", "seis sigma", "six sigma", "lean",
        "operaciones", "crm", "productividad", "gestión de proyectos",
        "project management", "industrial engineering", "manufactura",
        "inventarios", "seguridad laboral", "ergonomía", "automatización de procesos"
    ],
    Career.SYSTEMS: [
        "redes", "network", "networking", "cisco", "infraestructura",
        "azure", "aws", "cloud computing", "cómputo en la nube", "seguridad",
        "ciberseguridad", "cybersecurity", "linux", "sysadmin", "virtualización",
        "virtualization", "arquitectura ti", "powershell", "active directory",
        "telecomunicaciones", "servidores", "datacenter", "firewall"
    ],
    Career.SOFTWARE: [
        "software", "programación", "programming", "desarrollo web",
        "frontend", "backend", "full stack", "fullstack", "javascript",
        "typescript", "python", "java", "c#", ".net", "c++", "react",
        "angular", "vue", "node", "django", "fastapi", "spring", "git",
        "github", "docker", "kubernetes", "devops", "api", "rest",
        "bases de datos", "database", "sql", "testing", "algoritmos",
        "data structures", "patrones de diseño", "arquitectura de software", "scrum"
    ],
    Career.AI: [
        "ia", "ai", "artificial intelligence", "inteligencia artificial",
        "machine learning", "deep learning", "aprendizaje automático",
        "redes neuronales", "neural network", "nlp", "llm", "generative ai",
        "ia generativa", "vertex ai", "watsonx", "tensorflow", "pytorch",
        "prompt engineering", "data science", "ciencia de datos", "pandas",
        "bigquery", "computer vision", "visión artificial", "mlops",
        "hugging face", "kaggle", "langchain"
    ]
}

class CareerClassifier:
    """
    Clasificador heurístico que determina a qué carreras de ingeniería aplica un curso.
    """

    @classmethod
    def classify(cls, title: str, description: str = "", tags: List[str] = None, hints: List[str] = None) -> List[Career]:
        assigned_codes = set()

        # 1. Procesar pistas directas (hints)
        if hints:
            for hint in hints:
                clean_hint = hint.strip().lower()
                for code in [Career.INDUSTRIAL, Career.SYSTEMS, Career.SOFTWARE, Career.AI]:
                    if code in clean_hint:
                        assigned_codes.add(code)

        # 2. Análisis por palabras clave en texto completo
        combined_text = f"{title} {description} {' '.join(tags or [])}".lower()

        for code, keywords in CAREER_KEYWORDS.items():
            for kw in keywords:
                # Búsqueda exacta del término o palabra clave
                if kw in combined_text:
                    assigned_codes.add(code)
                    break

        # 3. Fallback: Si no coincide con ninguna, asignar Software por defecto
        if not assigned_codes:
            assigned_codes.add(Career.SOFTWARE)

        # Retornar las instancias de Career desde la base de datos
        return list(Career.objects.filter(code__in=assigned_codes))
