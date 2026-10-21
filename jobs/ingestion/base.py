from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class RawJob:
    portal: str
    external_id: str
    title: str
    company_name: str
    url: str
    company_logo_url: Optional[str] = None
    country: str = "PE"
    city: str = "Lima"
    modality: str = "remoto"
    contract_type: str = "tiempo_completo"
    seniority: str = "junior"
    salary_currency: str = "PEN"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_visible: bool = False
    description: str = ""
    short_description: str = ""
    requirements_summary: str = ""
    tags: List[str] = field(default_factory=list)
    career_hints: List[str] = field(default_factory=list)
    published_at: Optional[datetime] = None

class BaseJobConnector(ABC):
    portal_id: str = ""
    portal_name: str = ""
    group: str = "general"
    tier: int = 1

    @abstractmethod
    def fetch_jobs(self, limit: Optional[int] = None) -> List[RawJob]:
        """Extrae vacantes estructuradas desde el portal externo."""
        pass
