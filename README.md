# v-lkan_25_11_25

Enterprise Knowledge Graph Extraction Benchmark (KGEB)

This repository contains a simple benchmark and prototype pipeline for entity
and relation extraction from semi-structured enterprise text.

Quick start
-----------
1. Create/activate Python venv and install dependencies (optional):

	 Windows cmd:
		 D:\\package\\venv310\\Scripts\\activate.bat
		 pip install -r requirements.txt

	 PowerShell:
		 D:\\package\\venv310\\Scripts\\Activate.ps1
		 pip install -r requirements.txt

2. Run extraction and evaluation:

	 python src\\extract_v2.py
	 python src\\evaluate.py

3. One-shot test (Linux/WSL):

	 sh run_test.sh

4. Run tests (using project venv):

	 D:\\package\\venv310\\Scripts\\python.exe -m pytest -q tests

Outputs
-------
- `entities_output.json` — entity extraction results
- `relations_output.json` — relation extraction results
- `evaluation_report.json` — evaluation summary (counts + schema compliance)

Notes
-----
- `src/extract_v2.py` is a robust extractor that handles malformed dates by
	setting the project status to `Unknown` instead of failing.
- This is a prototype: for better accuracy replace the rule-based approach
	with ML-based NER (spaCy/transformers) and extend relations in `relations.json`.

Contributing
------------
PRs welcome — consider adding relation schemas, more tests, and CI.