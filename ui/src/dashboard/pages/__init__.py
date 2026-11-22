import importlib
from typing import Callable, ClassVar
import panel as pn
import xarray as xr
import pkgutil

class Tab:
    title: ClassVar[str] = ""
    order: ClassVar[int] = 0
    page_cls: ClassVar[type[Page]]

    def render(self, ds: xr.Dataset):
        return f"[tab] {self.title}"

class Page:
    title: ClassVar[str] = ""
    order: ClassVar[int] = 0
    registry: ClassVar[dict[str, type[Page]]] = {}
    _tab_classes: ClassVar[list[type[Tab]]] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._tab_classes = []
        Page.registry[cls.__name__] = cls

    @classmethod
    def tab(cls, _tab_cls: type[Tab] | None = None, *, title: str | None = None) -> Callable:
        if cls is Page:
            raise TypeError("Cannot register tab to abstract Page")

        def decorator(tab_cls: type[Tab]) -> type[Tab]:
            if not issubclass(tab_cls, Tab):
                raise TypeError(f"{tab_cls.__name__} must be a subclass of Tab")

            tab_cls.title = title or tab_cls.title or tab_cls.__name__

            if tab_cls not in cls._tab_classes:
                cls._tab_classes.append(tab_cls)
            return tab_cls

        return decorator(_tab_cls) if _tab_cls is not None else decorator


    def __init__(self):
        self.tabs: list[Tab] = [tab_cls() for tab_cls in self._tab_classes]

    def render(self, ds: xr.Dataset):

        tabs = [
            (tab.title, tab.render(ds)) for tab in sorted(self.tabs, key=lambda t: t.order)
        ]

        return pn.ui.Tabs(
            *tabs,
            sizing_mode="stretch_width"
        )

pkg = importlib.import_module(__package__)
for info in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
    importlib.import_module(info.name)