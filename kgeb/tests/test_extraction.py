import json
from pathlib import Path
import pytest
from kgeb.extractor import run_extraction, read_documents

ROOT = Path(__file__).resolve().parent.parent

def test_run_extraction_creates_outputs(tmp_path):
    out_dir = tmp_path / "outputs"
    entities, relations = run_extraction(doc_path=ROOT / "documents.txt", output_dir=out_dir)
    # Entities should include Person and Company
    assert "Person" in entities
    assert any(p["name"] == "John Doe" for p in entities["Person"]) or len(entities["Person"])>0
    assert "Company" in entities
    assert out_dir.joinpath("entities_output.json").exists()
    assert out_dir.joinpath("relations_output.json").exists()


def test_entities_fields(tmp_path):
    out_dir = tmp_path / "outputs"
    entities, relations = run_extraction(doc_path=ROOT / "documents.txt", output_dir=out_dir)
    for p in entities.get("Person", []):
        assert "name" in p and "age" in p and "position" in p

