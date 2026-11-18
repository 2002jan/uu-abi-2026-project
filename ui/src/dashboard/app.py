import panel as pn

from dashboard.sidebar import Sidebar
from dashboard.utils.state import Results, AppState
import hvplot.xarray
import hvplot.pandas

from zarr_project.stats.qc import median_from_hist

pn.extension(sizing_mode="stretch_width", throttled=True)

state = AppState()
sidebar = Sidebar()
sidebar.state = state

def plot(df: Results | None):
    if df is None:
        return "No data yet"

    avg_in = df.mean.sortby(df.mean)

    avg = avg_in.hvplot.barh(
        x="sample",
        y="depth",
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
        y="depth",
        hover=False,
        text_align="right",
        text_color="white",
        responsive=True,
    )

    med_in = median_from_hist(df.hist)
    med_in = med_in.sort_values(by=["depth"])

    med = med_in.hvplot.barh(
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
        hover=False,
        text_align="right",
        text_color="white",
        responsive=True,
    )

    return pn.Column(avg,med, sizing_mode="stretch_width")


pn.ui.Page(
        title="Getting Started App",
        sidebar=[sidebar],
        main=[pn.bind(plot, state.param.data)],
).servable()


