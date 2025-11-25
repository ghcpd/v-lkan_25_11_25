import json
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime


def _match_entity(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    # Minimal matching: same 'name' when present
    if "name" in a and "name" in b and a["name"] and b["name"]:
        return a["name"] == b["name"]
    # fallback: compare any equal values
    for k in a.keys():
        if k in b and a[k] and b[k] and a[k] == b[k]:
            return True
    return False


class Evaluator:
    def __init__(self, schema_path: str):
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def schema_compliance(self, extracted: Dict[str, List[Dict[str, Any]]]) -> float:
        total = 0
        compliant = 0
        for etype, attrs in self.schema.items():
            for e in extracted.get(etype, []):
                total += 1
                expected_keys = attrs
                # compliance if at least one expected attribute is present and not null
                if any((k in e and e[k] not in (None, "")) for k in expected_keys):
                    compliant += 1
        return 0.0 if total == 0 else compliant / total

    def evaluate_entities(self, gold: Dict[str, List[Dict[str, Any]]], pred: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        tp = 0
        fp = 0
        fn = 0
        for etype in set(list(gold.keys()) + list(pred.keys())):
            gold_list = gold.get(etype, [])
            pred_list = pred.get(etype, [])
            matched = [False] * len(gold_list)
            for p in pred_list:
                found = False
                for i, g in enumerate(gold_list):
                    if not matched[i] and _match_entity(p, g):
                        matched[i] = True
                        found = True
                        tp += 1
                        break
                if not found:
                    fp += 1
            # any gold not matched are false negatives
            for i, g in enumerate(gold_list):
                if not matched[i]:
                    fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}

    def evaluate_relations(self, gold: Dict[str, List[Dict[str, Any]]], pred: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        tp = 0
        fp = 0
        fn = 0
        for rtype in set(list(gold.keys()) + list(pred.keys())):
            gold_list = gold.get(rtype, [])
            pred_list = pred.get(rtype, [])
            matched = [False] * len(gold_list)
            for p in pred_list:
                found = False
                for i, g in enumerate(gold_list):
                    if not matched[i] and p == g:
                        matched[i] = True
                        found = True
                        tp += 1
                        break
                if not found:
                    fp += 1
            for i, g in enumerate(gold_list):
                if not matched[i]:
                    fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}

    def logical_consistency(self, entities: Dict[str, List[Dict[str, Any]]], relations: Dict[str, List[Dict[str, Any]]]) -> float:
        # basic check: relation participants reference existing entity names
        names_index = defaultdict(set)
        for etype, listv in entities.items():
            for e in listv:
                if 'name' in e and e['name']:
                    names_index[etype].add(e['name'])

        total_ref = 0
        valid_ref = 0
        for rtype, rels in relations.items():
            for r in rels:
                total_ref += 1
                # check if each value appears in any entity list (simple)
                ok = True
                for k, v in r.items():
                    found_any = any(v in names_index.get(et, set()) for et in names_index.keys())
                    if not found_any:
                        ok = False
                        break
                if ok:
                    valid_ref += 1

        return 0.0 if total_ref == 0 else valid_ref / total_ref

    def evaluate_all(self, gold_entities: Dict[str, List[Dict[str, Any]]], pred_entities: Dict[str, List[Dict[str, Any]]], gold_relations: Dict[str, List[Dict[str, Any]]], pred_relations: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        ent_metrics = self.evaluate_entities(gold_entities, pred_entities)
        rel_metrics = self.evaluate_relations(gold_relations, pred_relations)
        compliance = self.schema_compliance(pred_entities)
        consistency = self.logical_consistency(pred_entities, pred_relations)
        report = {
            "entity_precision": ent_metrics["precision"],
            "entity_recall": ent_metrics["recall"],
            "entity_f1": ent_metrics["f1"],
            "relation_precision": rel_metrics["precision"],
            "relation_recall": rel_metrics["recall"],
            "relation_f1": rel_metrics["f1"],
            "schema_compliance": compliance,
            "logical_consistency": consistency,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        return report
