import json
from collections import UserDict
from pathlib import Path
from typing import Any

import yaml


class Conf(UserDict[str, Any]):
    @classmethod
    def from_json(cls, filename: str) -> "Conf":
        return cls.from_file(filename, type="json")

    @classmethod
    def from_yaml(cls, filename: str) -> "Conf":
        return cls.from_file(filename, type="yaml")

    @classmethod
    def from_file(cls, filename: str, type: str = "json") -> "Conf":
        path = Path(filename)

        if path.exists() and path.is_file():
            with path.open() as file:
                if type == "json":
                    dict = json.load(file)
                elif type == "yaml":
                    dict = yaml.safe_load(file)
                else:
                    raise ValueError(f"Unknown Conf type: {type}. Supported: json.")
                return cls(dict)

        raise ValueError(
            f"Try to create Conf but {path.absolute()} doesn't exist or it's not a file."
        )
