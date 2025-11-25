import json
from datetime import datetime

def load_outputs(entities_path='entities_output.json', relations_path='relations_output.json'):
    with open(entities_path, encoding='utf-8') as f:
        entities = json.load(f)
    with open(relations_path, encoding='utf-8') as f:
        relations = json.load(f)
    return entities, relations

def schema_compliance(entities, schema):
    missing = []
    for k, attrs in schema.items():
        for ent in entities.get(k, []):
            for a in attrs:
                if a not in ent:
                    missing.append((k, a))
    total = sum(len(v) * len(schema[k]) for k, v in entities.items())
    compliance = 1 - (len(missing) / total) if total else 1.0
    return round(compliance, 4), missing

def simple_eval(entities, relations, schema):
    comp, missing = schema_compliance(entities, schema)
    issues = []
    names = set()
    for typ in entities.values():
        for ent in typ:
            if 'name' in ent:
                names.add(ent['name'])
    report = {
        'entity_count': {k: len(v) for k, v in entities.items()},
        'relation_count': {k: len(v) for k, v in relations.items()},
        'schema_compliance': f"{comp*100:.2f}%",
        'issues': issues,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    return report

if __name__ == '__main__':
    import sys
    schema = json.load(open('entities.json'))
    entities, relations = load_outputs()
    report = simple_eval(entities, relations, schema)
    with open('evaluation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print('Evaluation complete — wrote evaluation_report.json')
