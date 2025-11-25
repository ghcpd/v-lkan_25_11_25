# KGEB Quick Reference Guide

## 🚀 Installation

```bash
# Option 1: Bash Setup (Linux/Mac)
bash setup.sh
source venv/bin/activate

# Option 2: Windows Setup
setup.bat
venv\Scripts\activate

# Option 3: Docker
docker build -t kgeb .
docker run -it kgeb
```

## 📝 Common Commands

### Run Full Pipeline
```bash
python main.py run
```

### Extract Entities Only
```bash
python main.py extract-entities --documents documents.txt
```

### Extract Relations Only
```bash
python main.py extract-relations --documents documents.txt
```

### Evaluate Results
```bash
python main.py evaluate --method "My Method"
```

### Run Tests
```bash
python main.py test
# or with verbose output
python main.py test -v
```

### Show Statistics
```bash
python main.py stats
```

### Show Project Info
```bash
python main.py info
```

## 🔧 Advanced Usage

### Custom Paths
```bash
python main.py run \
  --documents my_documents.txt \
  --method "Advanced Method v2" \
  --output-dir results/experiment1
```

### With Ground Truth
```bash
python main.py evaluate \
  --entities-predicted output/entities_output.json \
  --relations-predicted output/relations_output.json \
  --entities-gt ground_truth/entities.json \
  --relations-gt ground_truth/relations.json
```

### Shell Scripts
```bash
# Run full pipeline with logging
bash run_pipeline.sh

# Run tests with coverage
bash run_test.sh

# One-click setup and run
bash quick_start.sh
```

## 📊 Expected Output

### Entities Output (entities_output.json)
```json
{
  "Person": [
    {
      "name": "John Doe",
      "age": 32,
      "position": "Researcher",
      "department": "R&D"
    }
  ],
  "Company": [
    {
      "name": "OpenAI",
      "industry": "Technology",
      "sector": "AI",
      "location": "San Francisco"
    }
  ]
}
```

### Relations Output (relations_output.json)
```json
{
  "WorksAt": [
    {
      "person": "John Doe",
      "company": "OpenAI",
      "position": "Researcher",
      "start_date": "Unknown"
    }
  ],
  "ManagesProject": [
    {
      "person": "John Doe",
      "project": "Alpha",
      "responsibility_level": "High"
    }
  ]
}
```

### Evaluation Report (evaluation_report.json)
```json
{
  "method": "KGEB Baseline",
  "timestamp": "2025-11-25T10:30:00",
  "entity_evaluation": {
    "schema_compliance": "90.00%",
    "total_entities": 150,
    "f1_score": 0.85,
    "precision": 0.88,
    "recall": 0.82
  },
  "relation_evaluation": {
    "schema_compliance": "75.00%",
    "total_relations": 320,
    "f1_score": 0.78
  }
}
```

## 🧪 Testing

### Run All Tests
```bash
pytest test_kgeb.py -v
```

### Run Specific Test Class
```bash
pytest test_kgeb.py::TestEntityExtractor -v
```

### Run with Coverage
```bash
pytest test_kgeb.py --cov=. --cov-report=html
```

### View Coverage Report
```bash
# Open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🐳 Docker Usage

### Build Image
```bash
docker build -t kgeb:latest .
```

### Run Pipeline
```bash
docker run -v $(pwd)/output:/app/output kgeb python main.py run
```

### Interactive Shell
```bash
docker run -it kgeb /bin/bash
```

### Run Tests in Docker
```bash
docker run kgeb python main.py test
```

## 📁 Directory Structure

```
KGEB/
├── documents.txt              # Input documents
├── entities.json              # Entity schema
├── relations.json             # Relation schema
│
├── entity_extractor.py        # Core module
├── relation_extractor.py      # Core module
├── evaluator.py               # Core module
├── main.py                    # CLI
│
├── test_kgeb.py              # Tests
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container
│
├── output/                    # Results
│   ├── entities_output.json
│   ├── relations_output.json
│   └── evaluation_report.json
│
├── logs/                      # Logs
└── test_results/              # Test reports
```

## 🔍 Troubleshooting

### spaCy Model Missing
```bash
python -m spacy download en_core_web_sm
```

### Permission Denied (Linux/Mac)
```bash
chmod +x *.sh
```

### Virtual Environment Not Activated
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

### Module Not Found
```bash
# Reinstall requirements
pip install -r requirements.txt
```

## 💡 Tips & Tricks

### 1. Check Progress
Monitor the output directory:
```bash
ls -lh output/
```

### 2. View Logs
```bash
tail -f logs/pipeline_*.log
```

### 3. Quick Stats
```bash
python main.py stats
```

### 4. Validate Output
```bash
cat output/entities_output.json | python -m json.tool
```

### 5. Compare Methods
```bash
# Method A
python main.py run --method "Method A" --output-dir output/method_a

# Method B
python main.py run --method "Method B" --output-dir output/method_b

# Compare
diff output/method_a/evaluation_report.json output/method_b/evaluation_report.json
```

## 📈 Performance Tips

### 1. Batch Processing
Process multiple documents in sequence:
```python
from main import KGEBPipeline

for doc in document_list:
    pipeline = KGEBPipeline(documents_path=doc)
    pipeline.run_full_pipeline()
```

### 2. Parallel Processing
Use multiprocessing for large datasets:
```python
from multiprocessing import Pool

with Pool(4) as p:
    p.map(process_document, document_list)
```

### 3. Memory Optimization
Process documents in chunks if memory is limited.

## 🎓 Learning Resources

- **README.md** - Full user guide
- **DEVELOPMENT.md** - Developer guide
- **PROJECT_SUMMARY.md** - Project overview
- **CHANGELOG.md** - Version history
- **test_kgeb.py** - Code examples

## 📞 Getting Help

1. Check the README.md
2. Run `python main.py info`
3. Run `python main.py --help`
4. Check test cases in test_kgeb.py
5. Open a GitHub issue

## ✅ Checklist Before Running

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy model downloaded
- [ ] Input file exists (`documents.txt`)
- [ ] Output directory writable

## 🎯 Quick Start Workflow

```bash
# 1. Setup (one time)
bash setup.sh
source venv/bin/activate

# 2. Run pipeline
python main.py run

# 3. Check results
python main.py stats
cat output/evaluation_report.json

# 4. Run tests
python main.py test
```

---

**Happy Knowledge Graph Extracting! 🚀**

For more details, see **README.md**
