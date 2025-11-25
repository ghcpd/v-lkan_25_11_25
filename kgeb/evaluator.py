from __future__ import annotations
import datetime as dt
from typing import Dict, Any, Tuple, List


def _flatten_entities(entities: Dict[str, List[Dict[str, Any]]]) -> List[Tuple[str, Tuple[Tuple[str, Any], ...]]]:
    flat = []
    for etype, items in entities.items():
        for item in items:
            normalized = tuple(sorted((k, _norm(v)) for k, v in item.items()))
            flat.append((etype, normalized))
    return flat


def _flatten_relations(relations: Dict[str, List[Dict[str, Any]]]) -> List[Tuple[str, Tuple[Tuple[str, Any], ...]]]:
    flat = []
    for rtype, items in relations.items():
        for item in items:
            normalized = tuple(sorted((k, _norm(v)) for k, v in item.items()))
            flat.append((rtype, normalized))
    return flat


def _norm(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip()
    return v


def precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate_entities(pred: Dict[str, Any], gold: Dict[str, Any]) -> Tuple[int, int, int]:
    pred_set = set(_flatten_entities(pred))
    gold_set = set(_flatten_entities(gold))
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    return tp, fp, fn


def evaluate_relations(pred: Dict[str, Any], gold: Dict[str, Any]) -> Tuple[int, int, int]:
    pred_set = set(_flatten_relations(pred))
    gold_set = set(_flatten_relations(gold))
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    return tp, fp, fn


def schema_compliance(pred_entities: Dict[str, Any], entity_schema: Dict[str, List[str]]) -> float:
    total = 0
    matched = 0
    for etype, items in pred_entities.items():
        allowed = set(entity_schema.get(etype, []))
        for item in items:
            for k in item.keys():
                total += 1
                if k in allowed:
                    matched += 1
    return (matched / total) * 100 if total else 100.0


ENTITY_ROLE_KEYS = {"person", "company", "project", "team", "department", "product", "client", "position", "technology", "location"}


def relation_entity_consistency(
    pred_relations: Dict[str, List[Dict[str, Any]]], pred_entities: Dict[str, List[Dict[str, Any]]]
) -> float:
    # Check that relation references exist in entities by name, for roles that map to entity types
    name_index = {}
    for etype, items in pred_entities.items():
        for item in items:
            name = item.get("name")
            if name:
                name_index.setdefault(etype, set()).add(str(name))
    total_refs = 0
    ok_refs = 0
    for rtype, items in pred_relations.items():
        for item in items:
            for role, ref in item.items():
                if role.lower() not in ENTITY_ROLE_KEYS:
                    continue  # skip non-entity references like industries, dates, etc.
                total_refs += 1
                ref_str = str(ref)
                ok = any(ref_str in names for names in name_index.values())
                if ok:
                    ok_refs += 1
    return (ok_refs / total_refs) * 100 if total_refs else 100.0


def evaluate(pred_entities, gold_entities, pred_relations, gold_relations, entity_schema) -> Dict[str, Any]:
    e_tp, e_fp, e_fn = evaluate_entities(pred_entities, gold_entities)
    r_tp, r_fp, r_fn = evaluate_relations(pred_relations, gold_relations)
    e_prec, e_rec, e_f1 = precision_recall_f1(e_tp, e_fp, e_fn)
    r_prec, r_rec, r_f1 = precision_recall_f1(r_tp, r_fp, r_fn)

    compliance = schema_compliance(pred_entities, entity_schema)
    consistency = relation_entity_consistency(pred_relations, pred_entities)

    return {
        "entity_precision": round(e_prec, 4),
        "entity_recall": round(e_rec, 4),
        "entity_f1": round(e_f1, 4),
        "relation_precision": round(r_prec, 4),
        "relation_recall": round(r_rec, 4),
        "relation_f1": round(r_f1, 4),
        "schema_compliance": f"{round(compliance, 2)}%",
        "logical_consistency": f"{round(consistency, 2)}%",
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
    }
