import hashlib
import json
from typing import Any, Dict

def compute_job_hash(job_dict: Dict[str, Any]) -> str:
    """
    Calcula un hash SHA-256 determinista a partir de los atributos clave de la vacante.
    Permite detectar cambios en el portal de origen y evitar actualizaciones redundantes.
    """
    keys_to_hash = [
        "title",
        "company_name",
        "url",
        "country",
        "city",
        "modality",
        "contract_type",
        "seniority",
        "salary_min",
        "salary_max",
        "salary_currency",
        "description",
        "short_description",
        "requirements_summary",
    ]
    normalized_data = {
        k: str(job_dict.get(k, "") or "").strip()
        for k in keys_to_hash
    }
    serialized = json.dumps(normalized_data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
