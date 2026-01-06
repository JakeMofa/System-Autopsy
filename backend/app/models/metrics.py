# app/models/metrics.py

from pydantic import BaseModel
from typing import List


class MetricPoint(BaseModel):
    time: int
    value: float


class MetricsBundle(BaseModel):
    latency_ms: List[MetricPoint]
    error_rate_pct: List[MetricPoint]
    request_volume: List[MetricPoint]
    queue_depth: List[MetricPoint]
