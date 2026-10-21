import re
from django.utils.text import slugify

# Patrón exhaustivo para identificar y remover emojis y pictogramas unicode
EMOJI_PATTERN = re.compile(
    "["
    "\U00010000-\U0010FFFF"  # Emojis suplementarios y símbolos (planos 1+)
    "\u2600-\u27BF"          # Símbolos misceláneos y dingbats
    "\u2300-\u23FF"          # Símbolos técnicos misceláneos
    "\u2B00-\u2BFF"          # Símbolos y flechas misceláneas
    "\u25A0-\u25FF"          # Formas geométricas
    "\uFE00-\uFE0F"          # Selectores de variación
    "\u200D"                # Zero width joiner
    "]+",
    flags=re.UNICODE
)

LEVEL_MAPPING = {
    "beginner": "beginner",
    "principiante": "beginner",
    "introductory": "beginner",
    "undergraduate": "beginner",
    "intro": "beginner",
    "intermediate": "intermediate",
    "intermedio": "intermediate",
    "advanced": "advanced",
    "avanzado": "advanced",
    "graduate": "advanced",
    "all": "all",
    "todos": "all",
}

def strip_emojis(text: str) -> str:
    """
    Remueve completamente cualquier emoji, icono pictográfico o símbolo tipográfico
    de una cadena de texto, garantizando nombres limpios y profesionales.
    """
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub("", text)
    return re.sub(r"\s+", " ", cleaned).strip()

def clean_text(text: str) -> str:
    """
    Limpia etiquetas HTML, elimina emojis y normaliza espacios en blanco repetidos.
    """
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = strip_emojis(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def normalize_level(raw_level: str) -> str:
    if not raw_level:
        return "beginner"
    lower = raw_level.strip().lower()
    for key, val in LEVEL_MAPPING.items():
        if key in lower:
            return val
    return "beginner"

def normalize_language(raw_lang: str) -> str:
    if not raw_lang:
        return "es"
    lower = raw_lang.strip().lower()
    if lower.startswith("es"):
        return "es"
    if lower.startswith("en"):
        return "en"
    return "other"

def generate_safe_slug(title: str, external_id: str = "", max_length: int = 150) -> str:
    clean_title = strip_emojis(title)
    base_slug = slugify(clean_title)[:max_length - 20]
    if not base_slug:
        base_slug = "curso"
    if external_id:
        clean_ext = slugify(strip_emojis(external_id))[:15]
        return f"{base_slug}-{clean_ext}"[:max_length]
    return base_slug[:max_length]
