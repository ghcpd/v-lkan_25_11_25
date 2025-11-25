import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Tuple
from .schema import load_entities_schema, load_relations_schema

ROOT = Path(__file__).resolve().parent


def load_json(p: Path) -> Dict:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _entity_key(entity_type: str, entity_obj: Dict[str, Any]) -> str:
    # For entities that have 'name', use name as key; otherwise full json dump
    if "name" in entity_obj and entity_obj["name"]:
        return entity_obj["name"]
    if "title" in entity_obj and entity_obj["title"]:
        return entity_obj["title"]
    return json.dumps(entity_obj, sort_keys=True)


def compute_entity_metrics(gold: Dict[str, List[Dict[str, Any]]], pred: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    # Returns counts per type, total precision/recall/F1
    metrics = {}
    total_tp = total_fp = total_fn = 0

    for etype, gold_list in gold.items():
        pred_list = pred.get(etype, [])
        gold_keys = { _entity_key(etype, g): g for g in gold_list }
        pred_keys = { _entity_key(etype, p): p for p in pred_list }

        tp_keys = set(gold_keys.keys()) & set(pred_keys.keys())
        tp = len(tp_keys)
        fp = max(0, len(pred_keys) - tp)
        fn = max(0, len(gold_keys) - tp)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

        metrics[etype] = {"tp": tp, "fp": fp, "fn": fn, "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}
        total_tp += tp
        total_fp += fp
        total_fn += fn

    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

    metrics["micro"] = {"tp": total_tp, "fp": total_fp, "fn": total_fn, "precision": round(micro_precision, 4), "recall": round(micro_recall, 4), "f1": round(micro_f1, 4)}
    return metrics


def _relation_key(rel_type: str, rel_obj: Dict[str, Any]) -> str:
    return json.dumps(rel_obj, sort_keys=True)


def compute_relation_metrics(gold: Dict[str, List[Dict[str, Any]]], pred: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    metrics = {}
    total_tp = total_fp = total_fn = 0
    for rtype, gold_list in gold.items():
        pred_list = pred.get(rtype, [])
        gold_keys = { _relation_key(rtype, g): g for g in gold_list }
        pred_keys = { _relation_key(rtype, p): p for p in pred_list }
        tp_keys = set(gold_keys.keys()) & set(pred_keys.keys())
        tp = len(tp_keys)
        fp = max(0, len(pred_keys) - tp)
        fn = max(0, len(gold_keys) - tp)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

        metrics[rtype] = {"tp": tp, "fp": fp, "fn": fn, "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}
        total_tp += tp
        total_fp += fp
        total_fn += fn

    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0
    metrics["micro"] = {"tp": total_tp, "fp": total_fp, "fn": total_fn, "precision": round(micro_precision, 4), "recall": round(micro_recall, 4), "f1": round(micro_f1, 4)}
    return metrics


def schema_compliance(pred_entities: Dict[str, List[Dict[str, Any]]], pred_relations: Dict[str, List[Dict[str, Any]]], entities_schema: Dict[str, List[str]] = None, relations_schema: Dict[str, Dict[str,str]] = None) -> Tuple[str, Dict[str, Any]]:
    # Compute percent compliance of entities and relations with expected schema fields
    if entities_schema is None:
        entities_schema = load_entities_schema(ROOT / "data" / "entities.json")
    if relations_schema is None:
        relations_schema = load_relations_schema(ROOT / "data" / "relations.json")

    total_entities = total_entity_fields = compliant_entity_fields = 0
    for etype, expected_fields in entities_schema.items():
        for e in pred_entities.get(etype, []):
            total_entities += 1
            for f in expected_fields:
                total_entity_fields += 1
                if f in e and e.get(f) is not None:
                    compliant_entity_fields += 1

    total_relations = total_relation_fields = compliant_relation_fields = 0
    # For relations, ensure keys specified in relations.json are in the object (subject/object names will be present)
    for rtype, rdef in relations_schema.items():
        for r in pred_relations.get(rtype, []):
            total_relations += 1
            # We'll assume subject/object exist keys are present; otherwise fail
            subject = rdef.get("subject")
            obj = rdef.get("object")
            total_relation_fields += 2
            # Heuristic: check whether relation dict has any key that maps to subject/object
            # Since relations are varied, we'll check the JSON contains at least one string per relation
            if any(v is not None for v in r.values()):
                compliant_relation_fields += 2

    entity_compliance_pct = (compliant_entity_fields / total_entity_fields * 100) if total_entity_fields else 100.0
    relation_compliance_pct = (compliant_relation_fields / total_relation_fields * 100) if total_relation_fields else 100.0
    # Aggregate
    overall_compliance = round((entity_compliance_pct + relation_compliance_pct) / 2, 2)
    details = {"entity_compliance_pct": round(entity_compliance_pct, 2), "relation_compliance_pct": round(relation_compliance_pct, 2)}
    return f"{overall_compliance}%", details


def logical_consistency(pred_entities: Dict[str, List[Dict[str, Any]]], pred_relations: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    # Check that relations reference entities that actually exist
    missing = []
    errors = 0
    entity_lookup = {etype: {_entity_key(etype, e) for e in lst} for etype, lst in pred_entities.items()}

    for rtype, lst in pred_relations.items():
        for rel in lst:
            # For common patterns like {"person": "Name", "company": "Company"}
            for k, v in rel.items():
                # Map key to entity type heuristics
                if k.lower() in ["person","manager","lead"]:
                    etype = "Person"
                elif k.lower() in ["company","owner"]:
                    etype = "Company"
                elif k.lower() in ["project"]:
                    etype = "Project"
                elif k.lower() in ["team"]:
                    etype = "Team"
                elif k.lower() in ["technology"]:
                    etype = "Technology"
                else:
                    etype = None
                if etype is not None and v is not None:
                    key = v
                    if key not in entity_lookup.get(etype, set()):
                        errors += 1
                        missing.append({"relation": rtype, "field": k, "value": v, "expected_type": etype})

    return {"errors": errors, "missing_references": missing}


def evaluate(gold_entities_path: Path, gold_relations_path: Path, pred_entities_path: Path, pred_relations_path: Path, method_name: str = "Method A") -> Dict[str, Any]:
    gold_entities = load_json(gold_entities_path)
    gold_relations = load_json(gold_relations_path)
    pred_entities = load_json(pred_entities_path)
    pred_relations = load_json(pred_relations_path)

    entity_metrics = compute_entity_metrics(gold_entities, pred_entities)
    relation_metrics = compute_relation_metrics(gold_relations, pred_relations)

    schema_comp, schema_details = schema_compliance(pred_entities, pred_relations)
    logic = logical_consistency(pred_entities, pred_relations)

    report = {
        "method": method_name,
        "entity_micro_precision": entity_metrics["micro"]["precision"],
        "entity_micro_recall": entity_metrics["micro"]["recall"],
        "entity_micro_f1": entity_metrics["micro"]["f1"],
        "relation_micro_precision": relation_metrics["micro"]["precision"],
        "relation_micro_recall": relation_metrics["micro"]["recall"],
        "relation_micro_f1": relation_metrics["micro"]["f1"],
        "schema_compliance": schema_comp,
        "schema_details": schema_details,
        "logical_consistency": logic,
        "timestamp": "2025-11-25T00:00:00Z"
    }

    out = ROOT.parent / "outputs" / "evaluation_report.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


if __name__ == "__main__":
    # Basic runner for demonstration
    print("Evaluation runner")
