# Enterprise Knowledge Graph Extraction Benchmark (KGEB)

This repo contains a small baseline rule-based system for extracting entities and relations from semi-structured enterprise text.

## Overview
- Designed to extract 10 entity types as defined in `kgeb/data/entities.json`.
- Relation types are in `kgeb/data/relations.json` (30 types — a combination of concrete and placeholder ones).
- Basic evaluator computes precision, recall, F1, schema compliance, and logical consistency.

## Quick start
1. Set up environment (Windows `cmd.exe`):

```cmd
setup.sh
```

2. Run extraction and evaluation:

```bash
# If using bash
./run_test.sh

# Or run CLI commands directly
python -m kgeb.cli extract --docs documents.txt --out outputs
python -m kgeb.cli eval kgeb/data/gold_entities.json kgeb/data/gold_relations.json outputs/entities_output.json outputs/relations_output.json --method "Baseline"
```

3. Run tests:

```cmd
pytest -q
```

## Outputs
- `outputs/entities_output.json` — extracted entities
- `outputs/relations_output.json` — extracted relations
- `outputs/evaluation_report.json` — evaluation report

## Extending the benchmark
- Replace rule-based extractor with ML model inference in `kgeb/extractor.py`.
- Create more comprehensive `gold` datasets in `kgeb/data`.
- Extend `kgeb/evaluator.py` with additional metrics and schema validations.

## License
MIT
