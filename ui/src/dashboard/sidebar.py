import asyncio

import panel as pn
import param
import pbzarr

import zarr_project as zp
import zarr_project.data
from dashboard.utils.state import Results, AppState
from dashboard.utils.dask import PanelProgress
import dask.array as da

from zarr_project.stats.qc import depth_histogram


class Sidebar(param.Parameterized):
    state = param.ClassSelector(class_=AppState)

    def __init__(self, **params):
        super().__init__(**params)

        self._dataset_selector = pn.ui.RadioButtonGroup(label='Select dataset', value=None, options=self._get_datasets(), orientation="vertical")
        self._button = pn.widgets.Button(name="Run", button_type="primary", on_click=self.run)
        self._bar = pn.indicators.Progress(value=0, max=100)
        self._status = pn.pane.Markdown("")

    def _get_datasets(self):
        datasets = zp.data.get_datasets()
        datasets = {d.name: d for d in datasets}

        return datasets

    def __panel__(self):
        return pn.Column(
            self._dataset_selector,
            pn.layout.Divider(),
            self._button,
            self._bar,
            self._status
        )

    def progress(self):
        return PanelProgress(self._bar, self._status)

    def compute(self, dataset):
        ds = zarr_project.data.load_dataset(dataset)
        # ds = pbzarr.region(ds, "LG1:0-1000")
        with self.progress():
            ds_mean = ds.depth.mean("position")
            hist = depth_histogram(ds.depth)

            res_mean, hist = da.compute(ds_mean, hist)

            return Results(res_mean, hist)

    async def run(self, event):
        self._button.disabled = True
        self._button.label = "Running..."
        try:
            self.state.data = await asyncio.to_thread(self.compute, self._dataset_selector.value)
        finally:
            self._button.disabled = False
            self._button.label = "Run"
