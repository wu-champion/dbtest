from typing import Dict, Any
from pathlib import Path

import yaml
import toml
import os
import csv


def read_yaml(path: str):
    with open(path, "r") as f:
        return yaml.full_load(f)


def dict2toml(path: str, file_name: str, data: Dict[str, any]) -> None:
    file_path = Path(path) / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as f:
        toml.dump(data, f)


def dict2file(path: str, file_name: str, data: Dict[str, Any]) -> None:
    file_path = Path(path) / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as f:
        for k, v in data.items():
            f.write(f"{k}\t{v}\n")


def dict2yaml(data: Dict, path: str, file_name: str):
    file_path = Path(path) / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf8") as f:
        yaml.dump(data, f)


def file2dict(path, file_name, delimiter="\t"):
    file = os.path.join(path, file_name)
    result = {}
    with open(file, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if len(row) == 2:
                key, value = row
                result.setdefault(key, []).append(value)
    return result
