@echo off
REM Run extraction and evaluation on Windows
python -m kgeb.extractor
python -m kgeb.evaluator "kgeb/data/gold_entities.json" "kgeb/data/gold_relations.json" "outputs/entities_output.json" "outputs/relations_output.json" "Method A"
echo Run completed
