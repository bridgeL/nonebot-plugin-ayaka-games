import json
from pathlib import Path


class LocalPath:
    def __init__(self, __file: str) -> None:
        self.path = Path(__file).parent

    def get_json_path(self, name: str):
        return self.path.joinpath(f"{name}.json")

    def load_json(self, name: str):
        path = self.get_json_path(name)
        return json.load(path.open("r", encoding="utf8"))
