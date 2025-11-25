#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
echo "Environment set up. Activate with: source .venv/bin/activate"