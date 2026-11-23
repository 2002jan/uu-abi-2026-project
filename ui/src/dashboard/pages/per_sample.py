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

    def render(self, ds: xr.Dataset):
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

@PerSamplePage.tab(title="Median")
class Median(Tab):
    order = 2

    def render(self, ds: xr.Dataset):
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

@PerSamplePage.tab(title="Breadth of Coverage")
class BreadthOfCoverage(Tab):
    order = 3

    def __init__(self):
        self.line_range_end = pn.ui.IntSlider(
            label="Depth range",
            start=2,
            end=20,
            step=1,
            value=20,
        )

        self.bar_depth_selector = pn.ui.RadioButtonGroup(
            label="Select depth (x)",
            value=1,
            options=[1,2,5,10,20],
            margin=(0,10,25,10)
        )

    def render(self, ds: xr.Dataset):
        sample_filter = pn.ui.MultiChoice(label="Filter samples", options=ds.sample.values.tolist())

        boc = breadth_of_coverage(ds.sample_histogram)
        max_depth = boc.sizes["depth_value"] - 1
        self.line_range_end.end = max_depth
        self.line_range_end.value = min(self.line_range_end.value, max_depth)

        line = pn.bind(self.render_line, boc, self.line_range_end, sample_filter)
        bar = pn.bind(self.render_bar, boc, self.bar_depth_selector, sample_filter)

        return pn.layout.Column(
            pn.Spacer(height=10),
            sample_filter,
            pn.layout.Divider(margin=(25,0,25,0)),
            self.line_range_end,
            line,
            pn.layout.Divider(margin=(25,0,25,0)),
            self.bar_depth_selector,
            bar
        )

    def render_line(self, boc: xr.DataArray, range_end: int, samples: list):
        boc = boc.sel(depth_value=slice(1, range_end))

        if len(samples) > 0:
            boc = boc.sel(sample=samples)

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

    def render_bar(self, boc: xr.DataArray, depth: int, samples: list):
        height = max(30 * (len(samples) if len(samples) > 0 else boc.sizes["sample"]), 200)

        if len(samples) > 0:
            boc = boc.sel(sample=samples)

        boc = boc.sel(depth_value=depth)
        boc = boc.sortby(boc, ascending=True)


        return (boc.hvplot.barh(
            x = "sample",
            y = "breadth",
            xlabel = "Sample",
            ylabel = "Fraction of genome covered",
            title = f"Breadth of coverage at ≥{depth}x",
            height = height,
            responsive = True,
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