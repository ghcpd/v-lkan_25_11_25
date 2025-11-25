import json
from kgeb.entity_extractor import extract_entities
from kgeb.data_loader import load_text, load_json


def test_entity_counts(docs_path, entities_schema_path):
    text = load_text(docs_path)
    schema = load_json(entities_schema_path)
    entities, person_projects_map = extract_entities(text, schema)
    assert len(entities["Person"]) == 30
    assert len(entities["Company"]) == 30
    assert len(entities["Project"]) == 72
    # person->projects map size equals number of persons with projects
    assert len(person_projects_map) == 30


def test_schema_compliance(docs_path, entities_schema_path):
    from kgeb.evaluator import schema_compliance

    text = load_text(docs_path)
    schema = load_json(entities_schema_path)
    entities, _ = extract_entities(text, schema)
    compliance = schema_compliance(entities, schema)
    assert compliance == 100.0
