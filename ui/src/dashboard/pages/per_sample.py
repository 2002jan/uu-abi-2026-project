import param
import xarray as xr
import hvplot.xarray
import hvplot.pandas
import panel as pn

from dashboard.pages import Page, Tab
from zarr_project.stats.qc import median_from_hist, breadth_of_coverage


class PerSamplePage(Page):
    title = "Per sample"
    order = 1


@PerSamplePage.tab(title="Mean")
class Mean(Tab):
    order = 1

    @param.depends("state.data")
    def bar(self):
        ds = self.state.data
        avg_in = ds.sample_mean.sortby(ds.sample_mean)

        return (avg_in.hvplot.barh(
            x="sample",
            y="sample_mean",
            title="Avg depth per sample",
            xlabel="Sample",
            ylabel="Avg depth",
            height=800,
            responsive=True,
        ).opts(
            tools=["hover"],
            default_tools=[]
        ) * avg_in.hvplot.labels(
            x="sample",
            y="sample_mean",
            text="sample_mean",
            hover=False,
            text_align="right",
            text_color="white",
            responsive=True,
        )).opts(shared_axes=False)

    def __panel__(self):
        return self.bar


@PerSamplePage.tab(title="Median")
class Median(Tab):
    order = 2

    @param.depends("state.data")
    def bar(self):
        ds = self.state.data
        med_in = median_from_hist(ds.sample_histogram)
        med_in = med_in.sort_values(by=["depth"])

        return (med_in.hvplot.barh(
            x="sample",
            y="depth",
            title="Median depth per sample",
            xlabel="Sample",
            ylabel="Median depth",
            height=800,
            responsive=True,
        ).opts(
            tools=["hover"],
            default_tools=[]
        ) * med_in.hvplot.labels(
            x="sample",
            y="depth",
            text="depth",
            hover=False,
            text_align="right",
            text_color="white",
            responsive=True,
        )).opts(shared_axes=False)

    def __panel__(self):
        return self.bar


@PerSamplePage.tab(title="Breadth of Coverage")
class BreadthOfCoverage(Tab):
    order = 3
    depth = param.Selector(default=1, objects=[1, 2, 5, 10, 20])
    max_x = param.Integer(default=20, bounds=(2, 100))
    samples = param.ListSelector(default=[])
    boc = param.ClassSelector(class_=xr.DataArray)

    @param.depends("state.data", watch=True, on_init=True)
    def _on_data(self):
        ds = self.state.data
        if ds is None:
            self.boc = None
            return
        self.param.samples.objects = self.state.data.sample.values.tolist()
        self.samples = []
        self.boc = breadth_of_coverage(self.state.data.sample_histogram)

    def _selected(self):
        return self.boc.sel(sample=self.samples) if self.samples else self.boc

    @param.depends("boc", "max_x", "samples")
    def line(self):
        if self.boc is None:
            return "No data yet"

        boc = self._selected().sel(depth_value=slice(1, self.max_x))

        return boc.hvplot.line(
            x="depth_value",
            by="sample",
            responsive=True,
            height=600,
            xlabel="Minimum depth (x)",
            ylabel="Fraction of genome covered",
            title="Breadth of coverage",
            hover_cols=["sample"],
            legend=False,
        ).opts(
            tools=["hover"],
            default_tools=[]
        )

    @param.depends("state.data", "boc", "depth", "samples")
    def bar(self):
        if self.boc is None:
            return "No data yet"

        boc = self._selected().sel(depth_value=self.depth)
        boc = boc.sortby(boc, ascending=True)

        height = max(30 * boc.sizes["sample"], 200)

        return (boc.hvplot.barh(
            x="sample",
            y="breadth",
            xlabel="Sample",
            ylabel="Fraction of genome covered",
            title=f"Breadth of coverage at ≥{self.depth}x",
            height=height,
            responsive=True,
        ).opts(
            tools=["hover"],
            default_tools=[]
        ) * boc.hvplot.labels(
            x="sample",
            y="breadth",
            text="breadth",
            hover=False,
            text_align="right",
            text_color="white",
            responsive=True,
        )).opts(shared_axes=False)

    def __panel__(self):
        return pn.layout.Column(
            pn.Spacer(height=10),
            pn.ui.MultiChoice.from_param(self.param.samples, label="Filter by samples"),
            pn.layout.Divider(margin=(25, 0, 25, 0)),
            pn.ui.IntSlider.from_param(self.param.max_x, label="Depth range",),
            self.line,
            pn.layout.Divider(margin=(25, 0, 25, 0)),
            pn.ui.RadioButtonGroup.from_param(self.param.depth, label="Select depth (x)", margin=(0,10,25,10)),
            self.bar
        )
