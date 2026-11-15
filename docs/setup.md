# Setup guide

This guide gets the project running on a fresh machine: installing **uv**, creating the Python
environment, placing the data, and the day-to-day uv commands you will need.

> **TL;DR**
> 1. Install uv (once per machine), following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
> ```sh
> git clone <repo-url> && cd <repo>                   # 2. get the code
> uv sync                                             # 3. create .venv with the exact pinned packages
> # 4. place your dataset(s) in data/ (see "Data" below)
> uv run jupyter lab                                  # 5. start working
> ```

---

## 1. What is uv and why do we use it?

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager. It replaces
`pip`, `venv`, `pip-tools` and `pyenv` with one tool. In this project uv:

* **installs the right Python** (3.14, pinned in `.python-version`), even if the system doesn't have it,
* **creates a virtual environment** in `.venv/` that is isolated from your system Python,
* **installs the exact same package versions for everyone**, recorded in `uv.lock`,
* **runs commands inside that environment** with `uv run …`, so you never need to "activate" anything.

The files involved:

| File | What it is | Edit by hand? | Committed? |
|---|---|---|---|
| `pyproject.toml` | project metadata and the **direct** dependencies, with minimum versions | rarely; use `uv add` / `uv remove` | yes |
| `uv.lock` | the **full resolved** dependency tree with exact versions and hashes | **never** | yes |
| `.python-version` | the Python version uv uses for this project | rarely | yes |
| `.venv/` | the actual environment, rebuilt from the two files above | never | **no** |

`pyproject.toml` says *what we need*, `uv.lock` says *exactly what we got*, and `.venv/` is
disposable. You can always delete it and rebuild it with `uv sync`.

---

## 2. Install uv (once per machine)

Follow the official **[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)**
for your operating system. It covers the standalone installer as well as package managers
(Homebrew, WinGet, pipx, …) and explains how to update uv later.

Restart the terminal, then check:

```sh
uv --version          # this project was set up with uv 0.13.x
```

---

## 3. Get the code and create the environment

```sh
git clone <repo-url>
cd <repo>
uv sync
```

`uv sync` does all of the following:

1. reads `.python-version` and finds Python 3.14. If it isn't installed, uv **downloads it
   automatically** into its own cache, without touching your system Python.
2. creates `.venv/` in the project root,
3. installs every package from `uv.lock`, **including the `dev` group** (JupyterLab, ipykernel),
4. installs this project's own package (`src/zarr_project`) in **editable mode**, so
   `import zarr_project` works everywhere and code changes take effect without reinstalling.

Useful variants:

```sh
uv sync --locked      # fail instead of updating uv.lock if it is out of date (good for CI / sanity checks)
uv sync --no-dev      # skip JupyterLab etc. (e.g. on a cluster where you only run scripts)
```

Check that it worked:

```sh
uv run python -c "import pbzarr, xarray, dask; print('ok')"
```

---

## 4. Data

All datasets live in the `data/` folder, which is **not in git**. Genomic datasets are typically
far too large for version control, so `data/` is git-ignored apart from a placeholder file
(`data/.gitkeep`) that keeps the folder in the repository. Each user places the datasets they work
with there manually.

```
data/
├── .gitkeep
├── <dataset>/              # e.g. a Zarr / PBZ store, BAM/BED files, …
└── <another-dataset>/
```

Copy a dataset in, or symlink it to avoid duplicating large files on the same machine:

```sh
cp -r /path/to/<dataset> data/
ln -s /path/to/<dataset> data/<dataset>
```

Anything the code generates (caches, intermediate results) also goes under `data/`, so it stays
out of git automatically.

---

## 5. Working in the project

### Running code: `uv run`

`uv run <command>` runs any command inside the project environment. It also checks first that
`.venv` matches `uv.lock` and syncs it if needed, so you never work in a stale environment.

```sh
uv run python script.py
uv run python -c "import xarray; print(xarray.__version__)"
uv run jupyter lab
```

You *can* activate the environment the classic way instead (`source .venv/bin/activate` on
Linux/macOS, `.venv\Scripts\activate` on Windows) and then use `python` / `jupyter` directly.
Just remember to `deactivate` afterwards.

### Jupyter

```sh
uv run jupyter lab
```

JupyterLab runs from the project environment, so the default **Python 3 (ipykernel)** kernel
already sees all packages. Notes:

* Put notebooks in `notebooks/`. **Notebooks are not committed for now**: `*.ipynb` is
  git-ignored, and only the empty `notebooks/` folder is tracked.
* Notebooks in `notebooks/` reach the data via a relative path, e.g. `"../data/<dataset>"`.
* To use code from `src/zarr_project/` in a notebook and pick up edits without restarting:

  ```python
  %load_ext autoreload
  %autoreload 2
  import zarr_project
  ```

* **Using an external Jupyter** (e.g. a system-wide install): register the environment as a
  named kernel once, then pick "zarr-project" in the kernel menu:

  ```sh
  uv run python -m ipykernel install --user --name zarr-project --display-name "zarr-project"
  ```

### IDEs

Point the IDE to the interpreter at **`.venv/bin/python`** (Windows: `.venv\Scripts\python.exe`).

* **VS Code:** *Python: Select Interpreter*, then pick `./.venv/bin/python`. For notebooks, choose
  the same interpreter as the kernel.
* **PyCharm:** *Settings → Project → Python Interpreter → Add → Existing*, then select
  `.venv/bin/python`. Recent PyCharm versions also detect uv projects automatically.

---

## 6. Managing dependencies

**Always use uv commands, not `pip install`.** pip changes `.venv` without updating
`pyproject.toml` / `uv.lock`, so your teammates won't get the package, and the next `uv sync`
removes it.

| Task | Command |
|---|---|
| add a package | `uv add numpy` |
| add with a version constraint | `uv add "pandas>=3.0"` |
| add a dev-only tool (not needed to run the analysis) | `uv add --dev ruff` |
| remove a package | `uv remove numpy` |
| see the dependency tree | `uv tree` (or `uv tree --depth 1`) |
| upgrade one package to the newest allowed version | `uv lock --upgrade-package xarray && uv sync` |
| upgrade everything | `uv lock --upgrade && uv sync` |
| try a tool once without adding it | `uv run --with seaborn python …` or `uvx ruff check .` |

`uv add` / `uv remove` update `pyproject.toml` **and** `uv.lock` **and** `.venv` in one step.

**Commit `pyproject.toml` and `uv.lock` together** whenever either changes. After pulling
changes that touch them, run `uv sync`. `uv run` also does this automatically.

> Declare what you import. If code imports a package directly (e.g. `numpy`, `pandas`, `zarr`),
> add it with `uv add` even if it is already installed as a dependency of something else.
> Otherwise a future upgrade of that other package could silently drop it.

---

## 7. Project layout

```
.
├── pyproject.toml        # project metadata + dependencies
├── uv.lock               # exact pinned versions (generated; commit it, don't edit it)
├── .python-version       # Python version for uv (3.14)
├── README.md
├── docs/                 # documentation (this file, notes, reports)
├── src/zarr_project/     # reusable project code (importable as `zarr_project`)
├── notebooks/            # Jupyter notebooks (local only; *.ipynb is git-ignored)
├── data/                 # input data + generated caches (git-ignored; see section 4)
└── .venv/                # virtual environment (generated by `uv sync`; git-ignored)
```

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `uv: command not found` after installing | restart the terminal; if it persists, see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) |
| `No interpreter found for Python 3.14` | `uv python install 3.14` (uv normally does this automatically; it can fail offline) |
| `The lockfile needs to be updated` with `--locked` | someone changed `pyproject.toml` without re-locking: run `uv lock`, then commit `uv.lock` |
| `ModuleNotFoundError` in Jupyter | the notebook uses the wrong kernel. Start Jupyter with `uv run jupyter lab`, or select the `.venv` / "zarr-project" kernel |
| something is weird with the environment | `rm -rf .venv && uv sync` rebuilds it from scratch (safe: `.venv` holds nothing of yours) |
| `FileNotFoundError` for a dataset | check it is in `data/` (section 4); notebooks use `../data/…`, scripts run from the repo root use `data/…` |
| computations run out of memory | reduce data before `.compute()`, process it in smaller pieces, or limit Dask workers: `dask.config.set(num_workers=4)` |

---

## 9. Command cheat sheet

```sh
uv sync                       # create/update .venv from uv.lock
uv run <cmd>                  # run anything inside the environment
uv run jupyter lab            # start JupyterLab
uv add <pkg> / uv remove <pkg>
uv add --dev <pkg>            # dev-only dependency
uv lock --upgrade-package <pkg>
uv tree                       # what is installed and why
uv python list                # Python versions uv can see
uv self update                # update uv itself
```
