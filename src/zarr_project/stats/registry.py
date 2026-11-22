from dataclasses import dataclass
from typing import Callable
from zarr_project.stats.models import Params

import xarray as xr

MetricFunc = Callable[[xr.Dataset, Params], xr.DataArray]

@dataclass(frozen=True)
class Metric:
    name: str
    func: MetricFunc
    version: int = 1

REGISTRY: dict[str, Metric] = {}

def metric(*, version: int = 1, name: str | None = None):
    def decorator(func: MetricFunc) -> MetricFunc:
        m = Metric(name=name or func.__name__, func=func, version=version)
        if m.name in REGISTRY:
            raise ValueError(f"metric {m.name!r} registered twice")

        REGISTRY[m.name] = m
        return func
    return decorator