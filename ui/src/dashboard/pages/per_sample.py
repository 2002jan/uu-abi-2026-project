import xarray as xr
import hvplot.xarray
import hvplot.pandas

from dashboard.pages import Page, Tab
from zarr_project.stats.qc import median_from_hist


class PerSamplePage(Page):
    title = "Per sample"
    order = 1


@PerSamplePage.tab(title="Mean")
class Mean(Tab):
    order = 1

    def render(self, ds: xr.Dataset):
        avg_in = ds.sample_mean.sortby(ds.sample_mean)

        return avg_in.hvplot.barh(
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
        )

@PerSamplePage.tab(title="Median")
class Median(Tab):
    order = 2

    def render(self, ds: xr.Dataset):
        med_in = median_from_hist(ds.sample_histogram)
        med_in = med_in.sort_values(by=["depth"])

        return med_in.hvplot.barh(
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
        )
