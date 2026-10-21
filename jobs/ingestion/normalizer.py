import re
from django.utils.text import slugify
from courses.ingestion.normalizer import strip_emojis, clean_text

def normalize_modality(raw_text: str) -> str:
    if not raw_text:
        return "remoto"
    lower = raw_text.lower()
    if any(k in lower for k in ["remot", "remote", "teletrabajo", "home office"]):
        return "remoto"
    if any(k in lower for k in ["hibrid", "hybrid", "semipresencial"]):
        return "hibrido"
    if any(k in lower for k in ["presencial", "on-site", "onsite", "en oficina"]):
        return "presencial"
    return "remoto"

def normalize_seniority(raw_text: str) -> str:
    if not raw_text:
        return "junior"
    lower = raw_text.lower()
    if any(k in lower for k in ["practicante", "trainee", "intern", "pasant", "becario"]):
        return "practicante"
    if any(k in lower for k in ["junior", "jr", "entry", "inicial"]):
        return "junior"
    if any(k in lower for k in ["semi senior", "ssr", "semi-senior", "intermedio", "mid"]):
        return "semi_senior"
    if any(k in lower for k in ["lead", "architect", "arquitecto", "principal", "director", "head", "gerente"]):
        return "lead"
    if any(k in lower for k in ["senior", "sr", "avanzado", "expert"]):
        return "senior"
    return "junior"

def normalize_contract_type(raw_text: str) -> str:
    if not raw_text:
        return "tiempo_completo"
    lower = raw_text.lower()
    if any(k in lower for k in ["preprofesional", "pre-profesional", "pre profesional"]):
        return "practicas_pre"
    if any(k in lower for k in ["profesional", "practicante profesional"]):
        return "practicas_pro"
    if any(k in lower for k in ["medio tiempo", "part time", "part-time", "parcial"]):
        return "medio_tiempo"
    if any(k in lower for k in ["freelance", "proyecto", "contractor", "por horas"]):
        return "freelance"
    if any(k in lower for k in ["temporal", "plazo fijo", "reemplazo"]):
        return "temporal"
    return "tiempo_completo"

def generate_safe_job_slug(company: str, title: str, external_id: str = "", max_length: int = 220) -> str:
    clean_company = strip_emojis(company)
    clean_title = strip_emojis(title)
    base = slugify(f"{clean_company}-{clean_title}")[:max_length - 25]
    if not base:
        base = "vacante-empleo"
    if external_id:
        clean_ext = slugify(strip_emojis(external_id))[:15]
        return f"{base}-{clean_ext}"[:max_length]
    return base[:max_length]
