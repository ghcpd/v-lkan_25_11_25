@echo off
REM Windows batch runner
set PY=python
set SCHEMA=entities.json
set REL=relations.json
set DOCS=documents.txt

echo Extracting entities...
%PY% -m kgeb.cli extract_entities --schema "%SCHEMA%" --docs "%DOCS%" --out entities_output.json
echo Extracting relations...
%PY% -m kgeb.cli extract_relations --relations "%REL%" --docs "%DOCS%" --out relations_output.json

echo Running evaluation with test gold
%PY% -m kgeb.cli evaluate --schema "%SCHEMA%" --gold_entities tests/gold_entities.json --pred_entities entities_output.json --gold_relations tests/gold_relations.json --pred_relations relations_output.json --out evaluation_report.json

echo outputs written: entities_output.json relations_output.json evaluation_report.json
