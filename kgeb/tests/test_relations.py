from pathlib import Path
from kgeb.extractor import run_extraction

ROOT = Path(__file__).resolve().parent.parent

def test_relation_manages_in_output(tmp_path):
    out_dir = tmp_path / "outputs"
    entities, relations = run_extraction(doc_path=ROOT / "documents.txt", output_dir=out_dir)
    # Relations should include Manages or EmployedBy
    assert "Manages" in relations
    assert isinstance(relations.get("Manages"), list)
    # If John Doe manages some project, ensure relation captured
    if any(m.get("person") == "John Doe" for m in relations.get("Manages", [])):
        assert True
    else:
        # If not found, at least EmployedBy should be present
        assert any(m.get("person") == "John Doe" for m in relations.get("EmployedBy", []))
