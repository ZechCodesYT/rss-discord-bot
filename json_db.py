import json
import pathlib
import contextlib
from typing import Any


class JSON_DB:
    def __init__(self, project_path: str):
        self.db_path = pathlib.Path(project_path).parent / "db.json"
        self.data = self._load_data()

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
        print("I've saved the database successfully")

    def save(self):
        with open(self.db_path, "w") as json_file:
            json.dump(self.data, json_file)

    def set(self, field: str, value: Any):
        self.data[field] = value

    def get(self, field: str, *, default: Any = None) -> Any:
        return self.data.get(field, default)

    def has(self, field: str) -> bool:
        return field in self.data

    def _load_data(self) -> dict[str, Any]:
        with contextlib.ExitStack() as stack:
            try:
                json_file = open(self.db_path)
            except FileNotFoundError:
                return {}
            else:
                stack.enter_context(json_file)
                return json.load(json_file)
