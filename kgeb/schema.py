import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_entities_schema(path=None):
    path = Path(path) if path else ROOT / "data" / "entities.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_relations_schema(path=None):
    path = Path(path) if path else ROOT / "data" / "relations.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
