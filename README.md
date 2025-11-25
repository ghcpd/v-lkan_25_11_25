# Enterprise Knowledge Graph Extraction Benchmark (KGEB)

This repository contains a small reproducible benchmark for entity and relation extraction on semi-structured enterprise text.

Quick start
1. Create a Python virtualenv and install requirements:

	python -m venv venv
	venv\Scripts\activate  (Windows)
	source venv/bin/activate (macOS / Linux)
	python -m pip install -r requirements.txt

2. Run the example extraction & evaluation (Unix):

	./run_test.sh

	Windows (cmd):

	run_test.bat

3. Run tests:

	pytest -q
