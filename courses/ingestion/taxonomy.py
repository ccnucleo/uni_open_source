from typing import List, Optional
from courses.models import Category, Tag

CATEGORY_KEYWORD_RULES = [
    (["frontend", "html", "css", "react", "vue", "angular", "responsive", "web design"], "Desarrollo Web (Frontend)"),
    (["backend", "api", "node", "django", "express", "fastapi", "spring", "flask"], "Desarrollo Web (Backend)"),
    (["full stack", "fullstack", "web development"], "Full Stack"),
    (["database", "sql", "postgresql", "mysql", "mongodb", "relational", "databases"], "Bases de Datos y SQL"),
    (["data science", "machine learning", "deep learning", "ai", "artificial intelligence", "pandas", "data analysis", "neural", "computation"], "Ciencia de Datos e IA"),
    (["security", "cybersecurity", "ciberseguridad", "cryptography", "hacking", "redes"], "Ciberseguridad y Redes"),
    (["devops", "cloud", "docker", "kubernetes", "aws", "azure", "linux", "git"], "DevOps y Cloud Computing"),
    (["algorithms", "data structures", "logic", "matematica", "mathematics", "discrete", "programming", "python", "javascript", "c#", "java"], "Fundamentos y Lógica"),
    (["mobile", "android", "ios", "flutter", "react native"], "Desarrollo Móvil"),
    (["architecture", "software engineering", "design patterns"], "Arquitectura de Software"),
]

class TaxonomyResolver:
    """
    Resuelve y asocia Categorías y Etiquetas existentes o nuevas para los cursos.
    Tolerante a duplicados heredados usando filtrado seguro.
    """

    @classmethod
    def resolve_category(cls, title: str, category_hint: Optional[str] = None, tags: Optional[List[str]] = None) -> Category:
        haystack = f"{title} {category_hint or ''} {' '.join(tags or [])}".lower()

        # 1. Búsqueda por reglas de palabras clave
        for keywords, target_category_name in CATEGORY_KEYWORD_RULES:
            if any(kw in haystack for kw in keywords):
                category = Category.objects.filter(name=target_category_name).first()
                if not category:
                    category = Category.objects.create(name=target_category_name)
                return category

        # 2. Si category_hint viene especificado y coincide directamente
        if category_hint:
            matched = Category.objects.filter(name__icontains=category_hint.strip()).first()
            if matched:
                return matched

        # 3. Fallback a categoría por defecto
        fallback_cat = Category.objects.filter(name="Fundamentos y Lógica").first()
        if not fallback_cat:
            fallback_cat = Category.objects.create(name="Fundamentos y Lógica")
        return fallback_cat

    @classmethod
    def resolve_tags(cls, raw_tags: List[str]) -> List[Tag]:
        tag_objects = []
        for raw in raw_tags:
            cleaned = raw.strip().lower()
            if not cleaned or len(cleaned) > 50:
                continue
            cleaned = cleaned.replace("#", "")
            tag_obj = Tag.objects.filter(name=cleaned).first()
            if not tag_obj:
                tag_obj = Tag.objects.create(name=cleaned)
            tag_objects.append(tag_obj)
        return tag_objects
