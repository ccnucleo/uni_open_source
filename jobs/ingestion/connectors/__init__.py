from typing import Dict, List, Type
from jobs.ingestion.base import BaseJobConnector
from .getonbrd import GetOnBrdConnector
from .remoteok import RemoteOkConnector
from .empleos_peru import EmpleosPeruConnector
from .computrabajo_peru import ComputrabajoPeruConnector

AVAILABLE_JOB_CONNECTORS: Dict[str, Type[BaseJobConnector]] = {
    GetOnBrdConnector.portal_id: GetOnBrdConnector,
    RemoteOkConnector.portal_id: RemoteOkConnector,
    EmpleosPeruConnector.portal_id: EmpleosPeruConnector,
    ComputrabajoPeruConnector.portal_id: ComputrabajoPeruConnector,
}

def get_job_connectors_by_group(group: str) -> List[Type[BaseJobConnector]]:
    return [c for c in AVAILABLE_JOB_CONNECTORS.values() if c.group == group]
