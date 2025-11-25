import json
from pathlib import Path


def write_json(obj, p):
    p = Path(p)
    p.parent.mkdir(exist_ok=True, parents=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def read_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)
