import argparse
import json
from .extractor import EntityExtractor
from .relation_extractor import RelationExtractor
from .evaluator import Evaluator


def run_entity_extract(schema_path: str, docs_path: str, out_path: str):
    ext = EntityExtractor(schema_path)
    entities = ext.extract_from_file(docs_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)


def run_relation_extract(rel_schema: str, docs_path: str, out_path: str):
    rel_ext = RelationExtractor(rel_schema)
    rels = rel_ext.extract_from_file(docs_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rels, f, indent=2)


def run_evaluation(schema_path: str, gold_entities_path: str, pred_entities_path: str, gold_relations_path: str, pred_relations_path: str, out_path: str):
    ev = Evaluator(schema_path)
    with open(gold_entities_path, "r", encoding="utf-8") as f:
        gold_e = json.load(f)
    with open(pred_entities_path, "r", encoding="utf-8") as f:
        pred_e = json.load(f)
    with open(gold_relations_path, "r", encoding="utf-8") as f:
        gold_r = json.load(f)
    with open(pred_relations_path, "r", encoding="utf-8") as f:
        pred_r = json.load(f)
    report = ev.evaluate_all(gold_e, pred_e, gold_r, pred_r)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def main():
    parser = argparse.ArgumentParser(prog="kgeb", description="KGEB extractor/evaluator CLI")
    sub = parser.add_subparsers(dest="cmd")

    ent = sub.add_parser("extract_entities")
    ent.add_argument("--schema", required=True)
    ent.add_argument("--docs", required=True)
    ent.add_argument("--out", default="entities_output.json")

    rel = sub.add_parser("extract_relations")
    rel.add_argument("--relations", required=True)
    rel.add_argument("--docs", required=True)
    rel.add_argument("--out", default="relations_output.json")

    evalp = sub.add_parser("evaluate")
    evalp.add_argument("--schema", required=True)
    evalp.add_argument("--gold_entities", required=True)
    evalp.add_argument("--pred_entities", required=True)
    evalp.add_argument("--gold_relations", required=True)
    evalp.add_argument("--pred_relations", required=True)
    evalp.add_argument("--out", default="evaluation_report.json")

    args = parser.parse_args()
    if args.cmd == "extract_entities":
        run_entity_extract(args.schema, args.docs, args.out)
    elif args.cmd == "extract_relations":
        run_relation_extract(args.relations, args.docs, args.out)
    elif args.cmd == "evaluate":
        run_evaluation(args.schema, args.gold_entities, args.pred_entities, args.gold_relations, args.pred_relations, args.out)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
