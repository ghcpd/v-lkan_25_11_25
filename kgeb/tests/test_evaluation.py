import json
from pathlib import Path
from kgeb.extractor import run_extraction
from kgeb.evaluator import evaluate

ROOT = Path(__file__).resolve().parent.parent

def test_evaluate_against_gold(tmp_path):
    # Generate predictions
    out_dir = tmp_path / "outputs"
    entities, relations = run_extraction(doc_path=ROOT / "documents.txt", output_dir=out_dir)
    p_entities_file = out_dir / "entities_output.json"
    p_relations_file = out_dir / "relations_output.json"

    # Use gold supplied in kgeb/data
    gold_e = ROOT / "data" / "gold_entities.json"
    gold_r = ROOT / "data" / "gold_relations.json"

    report = evaluate(gold_entities_path=gold_e, gold_relations_path=gold_r, pred_entities_path=p_entities_file, pred_relations_path=p_relations_file, method_name="TestMethod")
    assert "entity_micro_f1" in report
    assert "relation_micro_f1" in report
