import hashlib
import json
import shutil
from dataclasses import asdict
from pathlib import Path
import xarray as xr

from zarr_project.stats.models import Params
from zarr_project.stats.registry import Metric

CACHE_VERSION = 1 # Used to invalidate old version's cache when the changes are not caught by other fingerprints
CACHE_DIR = Path(".cache") / "qc"

class CacheEntry:
    def __init__(self, path: Path, params: Params, metric: Metric):
        self.ds_path = path
        self.params = params
        self.metric = metric

        if not (self.ds_path / "zarr.json").exists():
            raise ValueError(f"{self.ds_path} is not a valid zarr path")

        self.key = self._key()
        self.cache_path = self._get_cache_path()

    def _fingerprint(self):
        return hashlib.sha256((self.ds_path / "zarr.json").read_bytes()).hexdigest()

    def _key(self):
        key_data = {
            "fingerprint": self._fingerprint(),
            "name": self.metric.name,
            "params": [asdict(self.params)],
            "version": self.metric.version
        }

        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def _get_cache_path(self) -> Path:
        return CACHE_DIR / self.ds_path.name / f"{self.metric.name}_{self.key}.zarr"

    def is_cached(self) -> bool:
        return self.cache_path.exists()

    def try_load_cache(self):
        if not self.is_cached():
            return None

        return xr.open_zarr(self.cache_path, consolidated=False).load()[self.metric.name]

    def save(self, data: xr.DataArray):
        tmp = self.cache_path.with_suffix(".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        data.rename(self.metric.name).to_zarr(tmp, mode="w", consolidated=False)
        tmp.rename(self.cache_path)