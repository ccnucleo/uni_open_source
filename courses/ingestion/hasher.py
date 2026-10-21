import hashlib
import json
from typing import Any, Dict

def compute_course_hash(course_dict: Dict[str, Any]) -> str:
    """
    Calcula un hash SHA-256 determinista a partir de los atributos clave del curso.
    Si cualquiera de estos campos cambia en la fuente externa, el hash será diferente.
    """
    keys_to_hash = [
        "title",
        "description",
        "short_description",
        "url",
        "level",
        "resource_type",
        "has_certification",
        "language",
        "duration_hours",
        "instructor_name",
        "external_image_url",
        "provider_name",
        "credential_type",
        "is_free_credential",
        "has_practical_labs"
    ]
    normalized_data = {
        k: str(course_dict.get(k, "") or "").strip()
        for k in keys_to_hash
    }
    serialized = json.dumps(normalized_data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
