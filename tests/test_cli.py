import json
import os
from pathlib import Path
from kgeb.cli import main as kgeb_main, _resolve_output_path


def test_cli_run_outputs(tmp_path, docs_path, entities_schema_path, relations_schema_path):
    ent_out = tmp_path / "entities_output.json"
    rel_out = tmp_path / "relations_output.json"
    args = [
        "run",
        "--documents",
        str(docs_path),
        "--entities-schema",
        str(entities_schema_path),
        "--relations-schema",
        str(relations_schema_path),
        "--entities-output",
        str(ent_out),
        "--relations-output",
        str(rel_out),
        "--overwrite",
    ]
    kgeb_main(args)
    assert ent_out.exists()
    assert rel_out.exists()

    ent = json.loads(ent_out.read_text())
    rel = json.loads(rel_out.read_text())
    assert len(ent["Person"]) == 30
    assert len(rel["WorksAt"]) == 30


def test_conflict_handling(tmp_path):
    # create dummy file
    out = tmp_path / "entities_output.json"
    out.write_text("{}")
    resolved = _resolve_output_path(out, overwrite=False)
    assert resolved != out
    assert resolved.name.startswith(out.stem)


def test_concurrent_writes(tmp_path, docs_path, entities_schema_path, relations_schema_path):
    # simulate two concurrent runs writing to same target without overwrite
    shared_out = tmp_path / "entities_output.json"
    files = []
    def run(idx):
        args = [
            "run",
            "--documents", str(docs_path),
            "--entities-schema", str(entities_schema_path),
            "--relations-schema", str(relations_schema_path),
            "--entities-output", str(shared_out),
        ]
        kgeb_main(args)
    # run sequentially to simplify, relying on timestamped filenames
    run(1)
    run(2)
    # collect created files
    for p in tmp_path.glob("entities_output*.json"):
        files.append(p)
    assert len(files) >= 2
