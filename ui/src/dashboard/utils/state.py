import param

import xarray as xr


class AppState(param.Parameterized):
    data = param.ClassSelector(class_=xr.Dataset, allow_None=True, default=None)
