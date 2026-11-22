import dask
import xarray as xr

from zarr_project.cache import CacheEntry
from zarr_project.data import load_dataset
from zarr_project.stats.models import Params
from zarr_project.stats.registry import REGISTRY

def compute_stats(path, params: Params|None = None, use_cache: bool = True):
    params = params or Params()
    metrics = [CacheEntry(path, params, REGISTRY[n]) for n in REGISTRY]
    ds = load_dataset(path)

    results, missing = {}, []
    for m in metrics:
        cached = m.try_load_cache() if use_cache else None
        if cached is None:
            missing.append(m)
        else:
            results[m.metric.name] = cached

    if missing:
        lazy = {m.metric.name: m.metric.func(ds, params).rename(m.metric.name) for m in missing}
        (computed, ) = dask.compute(lazy)
        for m in missing:
            results[m.metric.name] = computed[m.metric.name]
            if use_cache:
                m.save(computed[m.metric.name])

    return xr.Dataset(results)