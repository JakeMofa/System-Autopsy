from pydantic import BaseModel
from typing import List


class ServiceNode(BaseModel):
    id: str
    name: str
    status: str


class DependencyEdge(BaseModel):
    source: str
    target: str


class SystemTopology(BaseModel):
    services: List[ServiceNode]
    dependencies: List[DependencyEdge]
