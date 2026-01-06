## app/models/topology
from pydantic import BaseModel
from typing import List


class ServiceNode(BaseModel):
    id: str
    name: str
    status: str

    latency_ms: float
    error_rate_pct: float


class DependencyEdge(BaseModel):
    source: str
    target: str


class SystemTopology(BaseModel):
    services: List[ServiceNode]
    dependencies: List[DependencyEdge]

