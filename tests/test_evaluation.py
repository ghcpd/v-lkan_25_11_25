import json
from kgeb.evaluator import evaluate


def test_evaluation_perfect_scores(project_root):
    pred_entities = json.loads((project_root / "data/gold/entities_output.json").read_text())
    pred_relations = json.loads((project_root / "data/gold/relations_output.json").read_text())
    gold_entities = pred_entities
    gold_relations = pred_relations
    entity_schema = json.loads((project_root / "entities.json").read_text())

    report = evaluate(pred_entities, gold_entities, pred_relations, gold_relations, entity_schema)
    assert report["entity_f1"] == 1.0
    assert report["relation_f1"] == 1.0
    assert report["schema_compliance"] == "100.0%"
    assert report["logical_consistency"] == "100.0%"
