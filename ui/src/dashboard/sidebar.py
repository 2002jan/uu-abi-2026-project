import asyncio

import panel as pn
import param

import zarr_project as zp
import zarr_project.data
from dashboard.utils.state import AppState
from zarr_project.stats.runner import compute_stats
from dashboard.utils.dask import PanelProgress

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
        # ds = zarr_project.data.load_dataset(dataset)
        # ds = pbzarr.region(ds, "LG1:0-1000")
        with self.progress():
            return compute_stats(dataset)

    async def run(self, event):
        if self._dataset_selector.value is None:
            return

        self._button.disabled = True
        self._button.label = "Running..."
        try:
            self.state.data = await asyncio.to_thread(self.compute, self._dataset_selector.value)
        finally:
            self._button.disabled = False
            self._button.label = "Run"
