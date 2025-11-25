import json
from kgeb.extractor import EntityExtractor
from kgeb.relation_extractor import RelationExtractor


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_entity_extraction_basic():
    ext = EntityExtractor('entities.json')
    entities = ext.extract_from_file('documents.txt')

    # The dataset contains John Doe, Jane Smith, Michael Brown
    names = {p.get('name') for p in entities.get('Person', [])}
    assert 'John Doe' in names
    assert 'Jane Smith' in names
    assert 'Michael Brown' in names

    companies = {c.get('name') for c in entities.get('Company', [])}
    assert 'OpenAI' in companies
    assert 'Google' in companies


def test_relation_extraction_basic():
    rel_ext = RelationExtractor('relations.json')
    relations = rel_ext.extract_from_file('documents.txt')

    works = relations.get('WorksAt') or []
    pairs = {(r.get('person'), r.get('company')) for r in works}
    assert ('John Doe', 'OpenAI') in pairs
    assert ('Jane Smith', 'Google') in pairs
