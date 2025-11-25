from typing import List, Dict, Tuple, Any


def merge_entities(lists: List[Dict[str, List[Dict[str, Any]]]]) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    """Merge multiple entity dictionaries (as returned by extractor) into a single canonical dict.

    Strategy: merge by entity 'name' when present; for attribute conflicts prefer the first non-null value.
    Returns (merged, conflicts) where conflicts is a list of conflict records.
    """
    merged = {}
    conflicts = []
    for d in lists:
        for etype, items in d.items():
            merged.setdefault(etype, {})
            for it in items:
                name = it.get('name')
                if name:
                    if name not in merged[etype]:
                        # store copy
                        merged[etype][name] = dict(it)
                    else:
                        # merge attributes
                        existing = merged[etype][name]
                        for k, v in it.items():
                            if k not in existing or existing.get(k) in (None, ""):
                                existing[k] = v
                            elif v not in (None, "") and v != existing.get(k):
                                # conflict
                                conflicts.append({"entity_type": etype, "name": name, "field": k, "value_existing": existing.get(k), "value_new": v})
    # convert merged[etype] maps back to lists
    out = {}
    for etype, dct in merged.items():
        out[etype] = list(dct.values())
    return out, conflicts
