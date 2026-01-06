from pydantic import BaseModel

from .metrics import MetricsBundle
from .topology import SystemTopology


class SimulationState(BaseModel):
    system_mode: str
    topology: SystemTopology
    metrics: MetricsBundle
