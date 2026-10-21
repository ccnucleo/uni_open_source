from typing import Dict, List, Type
from courses.ingestion.base import BaseCourseConnector
from .freecodecamp import FreeCodeCampConnector
from .mit_ocw import MitOcwConnector
from .microsoft_learn import MicrosoftLearnConnector
from .google_skills import GoogleSkillsConnector
from .kaggle_learn import KaggleLearnConnector
from .huggingface_learn import HuggingFaceLearnConnector
from .hubspot_academy import HubSpotAcademyConnector
from .talento_digital import TalentoDigitalConnector
from .the_odin_project import TheOdinProjectConnector

AVAILABLE_CONNECTORS: Dict[str, Type[BaseCourseConnector]] = {
    FreeCodeCampConnector.platform_id: FreeCodeCampConnector,
    MitOcwConnector.platform_id: MitOcwConnector,
    MicrosoftLearnConnector.platform_id: MicrosoftLearnConnector,
    GoogleSkillsConnector.platform_id: GoogleSkillsConnector,
    KaggleLearnConnector.platform_id: KaggleLearnConnector,
    HuggingFaceLearnConnector.platform_id: HuggingFaceLearnConnector,
    HubSpotAcademyConnector.platform_id: HubSpotAcademyConnector,
    TalentoDigitalConnector.platform_id: TalentoDigitalConnector,
    TheOdinProjectConnector.platform_id: TheOdinProjectConnector,
}

def get_connectors_by_group(group: str) -> List[Type[BaseCourseConnector]]:
    """Filtra conectores registrados según su grupo temático/origen."""
    return [c for c in AVAILABLE_CONNECTORS.values() if c.group == group]

def get_connectors_by_tier(tier: int) -> List[Type[BaseCourseConnector]]:
    """Filtra conectores por nivel de criticidad o prioridad."""
    return [c for c in AVAILABLE_CONNECTORS.values() if c.tier <= tier]
