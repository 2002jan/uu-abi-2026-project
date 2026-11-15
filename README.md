# Applied Bioinformatics project - Using advanced data formats to explore signals of sequencing coverage

## Quick start

```sh
uv sync                     # create the environment (Python 3.14 + pinned packages)
# copy the data to data/monkeyflower.pbz (not in git)
uv run jupyter lab
```

See **[docs/setup.md](docs/setup.md)** for the full setup guide: installing uv, the data
layout, Jupyter/IDE configuration and dependency management.

## Repository layout

| Path | Contents |
|---|---|
| `src/zarr_project/` | reusable project code |
| `docs/` | documentation |
| `notebooks/` | Jupyter notebooks |
| `data/` | input data and generated files (not committed) |
