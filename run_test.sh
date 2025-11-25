#!/usr/bin/env bash
# Simple runner for extract/evaluate (POSIX shell)
set -euo pipefail
PY=python
SCHEMA=entities.json
REL=relations.json
DOCS=documents.txt

echo "Extracting entities..."
$PY -m kgeb.cli extract_entities --schema "$SCHEMA" --docs "$DOCS" --out entities_output.json
echo "Extracting relations..."
$PY -m kgeb.cli extract_relations --relations "$REL" --docs "$DOCS" --out relations_output.json

echo "Running evaluation with test gold (tests/gold_entities.json and tests/gold_relations.json)"
$PY -m kgeb.cli evaluate --schema "$SCHEMA" --gold_entities tests/gold_entities.json --pred_entities entities_output.json --gold_relations tests/gold_relations.json --pred_relations relations_output.json --out evaluation_report.json

echo "Outputs: entities_output.json relations_output.json evaluation_report.json"
