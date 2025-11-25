import json
from kgeb.evaluator import Evaluator


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_evaluation_roundtrip():
    ev = Evaluator('entities.json')
    gold_entities = load('tests/gold_entities.json')
    gold_relations = load('tests/gold_relations.json')

    # run production extractors to get predictions
    from kgeb.extractor import EntityExtractor
    from kgeb.relation_extractor import RelationExtractor

    ext = EntityExtractor('entities.json')
    pred_entities = ext.extract_from_file('documents.txt')

    rel_ext = RelationExtractor('relations.json')
    pred_relations = rel_ext.extract_from_file('documents.txt')

    report = ev.evaluate_all(gold_entities, pred_entities, gold_relations, pred_relations)

    # At least ensure metrics were produced and are between 0 and 1
    assert 0.0 <= report['entity_f1'] <= 1.0
    assert 0.0 <= report['relation_f1'] <= 1.0
    # Schema compliance for our predictors should be present
    assert 0.0 <= report['schema_compliance'] <= 1.0
