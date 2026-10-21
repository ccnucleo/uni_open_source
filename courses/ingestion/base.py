from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RawCourse:
    platform: str
    external_id: str
    title: str
    url: str
    short_description: str = ""
    description: str = ""
    image_url: Optional[str] = None
    level: str = "beginner"            # "beginner", "intermediate", "advanced", "all"
    resource_type: str = "platform"     # "platform", "youtube", "docs"
    has_certification: bool = False
    language: str = "es"                # "es", "en", "other"
    duration_hours: Optional[float] = None
    instructor_name: str = ""
    category_hint: Optional[str] = None # Pista de categoría según la fuente
    tags: List[str] = field(default_factory=list)
    
    # Nuevos atributos de escalabilidad (Detalles páginas.md)
    provider_name: str = ""             # Ej: "Google Cloud", "Microsoft", "IBM", "AWS", "Cisco"
    credential_type: str = "none"       # "skill_badge", "certificate", "audit_access", "completion", "none"
    is_free_credential: bool = True     # True si la credencial formal es gratuita
    has_practical_labs: bool = False    # True si incluye laboratorios prácticos en la nube
    career_hints: List[str] = field(default_factory=list) # Ej: ["software", "ai", "sistemas", "industrial"]

class BaseCourseConnector(ABC):
    """
    Clase base para todos los conectores de proveedores de cursos.
    """
    platform_id: str = "unknown"
    platform_name: str = "Unknown Platform"
    group: str = "general"              # "api", "cloud", "ai", "national", "audit"
    tier: int = 1                       # 1: API oficial, 2: Catálogo estructurado, 3: Scraping

    @abstractmethod
    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        """
        Consulta la fuente externa y retorna una lista de objetos RawCourse normalizados.
        """
        pass

