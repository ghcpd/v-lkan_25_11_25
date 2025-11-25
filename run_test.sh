#!/bin/sh
python src/extract.py
python src/evaluate.py
echo "Done. Outputs: entities_output.json relations_output.json evaluation_report.json"
