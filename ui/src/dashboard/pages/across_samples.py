import xarray as xr

from dashboard.pages import Page

class AcrossSamplesPage(Page):
    title = "Across samples"
    order = 2

    def render(self, ds: xr.Dataset):
        return "TODO!"