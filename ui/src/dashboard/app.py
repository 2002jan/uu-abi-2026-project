import panel as pn

from dashboard.pages import Page
from dashboard.sidebar import Sidebar
from dashboard.utils.state import AppState
import xarray as xr


pn.extension(sizing_mode="stretch_width", throttled=True)

state = AppState()
sidebar = Sidebar()
sidebar.state = state


def render_page(page, df: xr.Dataset | None):
    if df is None:
        return "No data yet"

    return page.render(df)


main_area = pn.Column(
    ""
)

def switch_page(page: Page):
    main_area[:] = [pn.bind(render_page, page, state.param.data)]


def nav():
    pages = [p(state) for p in Page.registry.values()]
    pages.sort(key=lambda p: p.order)

    menu = pn.ui.TabMenu(
        items=[{"label": p.title} for p in pages],
        active=0,
        color="light",
        sizing_mode="fixed",
    )
    menu.param.watch(lambda e: switch_page(pages[e.new]), "active")


    switch_page(pages[0])

    return pn.Row(
        pn.layout.HSpacer(),
        menu,
        sizing_mode="stretch_width",
    )


pn.ui.Page(
    title="Getting Started App",
    sidebar=[sidebar],
    main=[main_area],
    header=[nav]
).servable()
