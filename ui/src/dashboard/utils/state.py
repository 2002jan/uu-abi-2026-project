from dataclasses import dataclass

import param
import xarray as xr


@dataclass
class Results:
    mean: xr.DataArray
    hist: xr.DataArray


class AppState(param.Parameterized):
    data = param.ClassSelector(class_=Results, allow_None=True, default=None)
