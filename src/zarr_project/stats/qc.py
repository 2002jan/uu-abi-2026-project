import numpy as np
import xarray as xr

from zarr_project.stats.models import Params
from zarr_project.stats.registry import metric

def _block_hist(block, max_depth):
    n_samples = block.shape[1]
    clipped = np.minimum(block, max_depth).astype(np.int64)
    idx = clipped + np.arange(n_samples) * (max_depth + 1)
    counts = np.bincount(idx.ravel(), minlength=n_samples * (max_depth + 1))
    return counts.reshape(1, n_samples, max_depth + 1)

def depth_histogram(depth: xr.DataArray, max_depth: int) -> xr.DataArray:
    data = depth.data.rechunk({1: -1}) # all samples in one chunk
    hist = data.map_blocks(
        _block_hist, max_depth,
        new_axis=2,
        chunks=((1,) * data.numblocks[0], (data.shape[1],), (max_depth + 1,)),
        dtype=np.int64,
    ).sum(axis=0)
    return xr.DataArray(
        hist, dims=("sample", "depth_value"),
        coords={"sample": depth.sample, "depth_value": np.arange(max_depth + 1)},
    )

def median_from_hist(hist: xr.DataArray) -> xr.DataArray:
    cdf = hist.cumsum("depth_value")
    n = cdf.isel(depth_value=-1)
    lo = (cdf > (n - 1) // 2).argmax("depth_value")
    hi = (cdf > n // 2).argmax("depth_value")
    median = (lo + hi) / 2

    return median.to_dataframe(name="depth").reset_index()

@metric(version=1)
def sample_mean(ds, params: Params):
    return ds.depth.mean("position")

@metric(version=1)
def sample_histogram(ds, params: Params):
    return depth_histogram(ds.depth, params.max_depth)