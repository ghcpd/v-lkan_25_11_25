from __future__ import annotations
import argparse
import sys
import datetime as dt
from pathlib import Path
from typing import List
from .data_loader import load_text, load_json, dump_json
from .entity_extractor import extract_entities
from .relation_extractor import extract_relations
from .evaluator import evaluate


def _read_documents(doc_paths: List[str]) -> str:
    contents = []
    for p in doc_paths:
        path = Path(p)
        if path.is_dir():
            for file in sorted(path.glob("**/*.txt")):
                contents.append(load_text(file))
        else:
            contents.append(load_text(path))
    return "\n".join(contents)


def _resolve_output_path(path: str | Path, overwrite: bool) -> Path:
    path = Path(path)
    if path.exists() and not overwrite:
        ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = path.with_name(f"{path.stem}_{ts}{path.suffix}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def cmd_extract_entities(args: argparse.Namespace) -> None:
    text = _read_documents(args.documents)
    schema = load_json(args.entities_schema)
    entities, person_projects_map = extract_entities(text, schema)
    out_path = _resolve_output_path(args.output, args.overwrite)
    dump_json(entities, out_path)
    if args.person_projects_map:
        dump_json({k: v for k, v in person_projects_map.items()}, args.person_projects_map)


def cmd_extract_relations(args: argparse.Namespace) -> None:
    text = _read_documents(args.documents)
    relations_schema = load_json(args.relations_schema)
    person_projects_map = None
    if args.person_projects_map and Path(args.person_projects_map).exists():
        person_projects_map = load_json(args.person_projects_map)
    relations = extract_relations(text, relations_schema, person_projects_map)
    out_path = _resolve_output_path(args.output, args.overwrite)
    dump_json(relations, out_path)


def cmd_run(args: argparse.Namespace) -> None:
    # end-to-end extraction
    text = _read_documents(args.documents)
    entity_schema = load_json(args.entities_schema)
    relation_schema = load_json(args.relations_schema)
    entities, person_projects_map = extract_entities(text, entity_schema)
    relations = extract_relations(text, relation_schema, person_projects_map)

    ent_out = _resolve_output_path(args.entities_output, args.overwrite)
    rel_out = _resolve_output_path(args.relations_output, args.overwrite)
    dump_json(entities, ent_out)
    dump_json(relations, rel_out)


def cmd_evaluate(args: argparse.Namespace) -> None:
    pred_entities = load_json(args.pred_entities)
    pred_relations = load_json(args.pred_relations)
    gold_entities = load_json(args.gold_entities)
    gold_relations = load_json(args.gold_relations)
    entity_schema = load_json(args.entities_schema)
    report = evaluate(pred_entities, gold_entities, pred_relations, gold_relations, entity_schema)
    out_path = _resolve_output_path(args.output, args.overwrite)
    dump_json(report, out_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kgeb", description="KGEB CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ent = sub.add_parser("extract-entities", help="Extract entities from documents")
    p_ent.add_argument("--documents", nargs="+", required=True, help="Text files or directories")
    p_ent.add_argument("--entities-schema", required=True, help="Path to entities.json")
    p_ent.add_argument("--output", default="entities_output.json")
    p_ent.add_argument("--overwrite", action="store_true")
    p_ent.add_argument("--person-projects-map", help="Optionally dump person->projects map")
    p_ent.set_defaults(func=cmd_extract_entities)

    p_rel = sub.add_parser("extract-relations", help="Extract relations from documents")
    p_rel.add_argument("--documents", nargs="+", required=True)
    p_rel.add_argument("--relations-schema", required=True)
    p_rel.add_argument("--output", default="relations_output.json")
    p_rel.add_argument("--overwrite", action="store_true")
    p_rel.add_argument("--person-projects-map", help="Optional precomputed person->projects map")
    p_rel.set_defaults(func=cmd_extract_relations)

    p_run = sub.add_parser("run", help="End-to-end extraction")
    p_run.add_argument("--documents", nargs="+", required=True)
    p_run.add_argument("--entities-schema", required=True)
    p_run.add_argument("--relations-schema", required=True)
    p_run.add_argument("--entities-output", default="entities_output.json")
    p_run.add_argument("--relations-output", default="relations_output.json")
    p_run.add_argument("--overwrite", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_eval = sub.add_parser("evaluate", help="Evaluate predictions against gold")
    p_eval.add_argument("--pred-entities", required=True)
    p_eval.add_argument("--pred-relations", required=True)
    p_eval.add_argument("--gold-entities", required=True)
    p_eval.add_argument("--gold-relations", required=True)
    p_eval.add_argument("--entities-schema", required=True)
    p_eval.add_argument("--output", default="evaluation_report.json")
    p_eval.add_argument("--overwrite", action="store_true")
    p_eval.set_defaults(func=cmd_evaluate)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
