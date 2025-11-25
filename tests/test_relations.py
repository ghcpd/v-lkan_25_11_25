from kgeb.data_loader import load_text, load_json
from kgeb.entity_extractor import extract_entities
from kgeb.relation_extractor import extract_relations


def test_relation_counts(docs_path, entities_schema_path, relations_schema_path):
    text = load_text(docs_path)
    entities, person_projects_map = extract_entities(text, load_json(entities_schema_path))
    relations = extract_relations(text, load_json(relations_schema_path), person_projects_map)

    assert len(relations["WorksAt"]) == 30
    assert len(relations["ManagesProject"]) == 72
    assert len(relations["ProjectHasDates"]) == 72
    assert len(relations["CompanyOperatesInIndustry"]) == 30
