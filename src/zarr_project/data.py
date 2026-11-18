import os
import pbzarr
from pathlib import Path

import xarray


def get_datasets():
    data_path: Path = Path("data/")

    datasets = os.listdir(data_path)
    datasets = list(filter(lambda x: x.endswith(".pbz"), datasets))
    datasets = list(map(lambda x: data_path / x, datasets))

    return datasets

def load_dataset(ds_path) -> xarray.Dataset:
    return pbzarr.open(ds_path)
