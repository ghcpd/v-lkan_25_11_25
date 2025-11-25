# KGEB Quick Reference Guide

## ⚡ One-Minute Setup

### Windows
```cmd
cd kgeb
setup.bat
run_test.bat data\documents.txt
```

### Linux/macOS
```bash
cd kgeb
bash setup.sh
bash run_test.sh data/documents.txt
```

### Docker
```bash
docker build -t kgeb .
docker run -v $(pwd)/output:/app/output kgeb
```

---

## 📋 Core Commands

| Task | Command |
|------|---------|
| **Full Pipeline** | `python src/pipeline.py documents.txt` |
| **Extract Entities** | `python src/entity_extractor.py documents.txt entities.json` |
| **Extract Relations** | `python src/relation_extractor.py documents.txt relations.json` |
| **Evaluate** | `python src/evaluator.py entities.json relations.json report.json` |
| **Run Tests** | `python tests/test_kgeb.py` |

---

## 🎯 Key Features

✅ **10 Entity Types** - Person, Company, Project, Department, Position, Technology, Location, Team, Product, Client

✅ **30 Relation Types** - WorksAt, ManagesProject, BelongsTo, OwnsProject, UsesTechnology, and 25 more

✅ **4 Evaluation Metrics** - Precision/Recall/F1, Schema Compliance, Logical Consistency, Weighted Score

✅ **Reproducible Environment** - Docker, virtualenv, requirements.txt

✅ **Automated Testing** - 20+ test cases covering all components

✅ **Comprehensive Reporting** - Structured JSON outputs with detailed metrics

---

## 📁 File Structure

```
kgeb/
├── src/
│   ├── entity_extractor.py      # Extract entities
│   ├── relation_extractor.py    # Extract relations
│   ├── evaluator.py             # Evaluate results
│   └── pipeline.py              # Orchestrate pipeline
├── tests/
│   └── test_kgeb.py             # Test suite
├── config/
│   ├── entities.json            # Entity schema
│   └── relations.json           # Relation schema
├── data/
│   └── documents.txt            # Sample input
├── output/                      # Generated outputs
├── README.md                    # Full documentation
├── CONFIGURATION_GUIDE.md       # Customization guide
├── TEST_REPORT_TEMPLATE.md      # Report format
└── PROJECT_INDEX.md             # Navigation guide
```

---

## 🚀 Quick Examples

### Basic Extraction
```bash
python src/pipeline.py documents.txt
# Outputs: entities_output.json, relations_output.json, evaluation_report.json
```

### Custom Method Name
```bash
python src/pipeline.py documents.txt "My Extraction Method"
```

### Python API
```python
from src.entity_extractor import EntityExtractor
from src.pipeline import KGEBPipeline

# Use pipeline
pipeline = KGEBPipeline()
report = pipeline.run_full_pipeline('documents.txt')

# Or individual components
extractor = EntityExtractor(schema)
entities = extractor.extract_all(text)
extractor.save_to_file('entities.json')
```

---

## 📊 Output Examples

### entities_output.json
```json
{
  "Person": [
    {"name": "John Doe", "age": 32, "position": "Researcher", "department": null}
  ],
  "Company": [
    {"name": "OpenAI", "industry": "Technology", "sector": "AI", "location": null}
  ],
  "Project": [
    {"name": "Alpha", "start_date": "2023-01-15", "end_date": "2023-06-30", "status": "Completed", "budget": null}
  ]
}
```

### evaluation_report.json
```json
{
  "method": "KGEB Pipeline",
  "timestamp": "2025-11-25T12:30:00Z",
  "overall_metrics": {
    "entity_f1": 0.85,
    "relation_f1": 0.78,
    "schema_compliance": 95.5,
    "logical_consistency": 92.0
  }
}
```

---

## 🧪 Testing

```bash
# Run all tests
python tests/test_kgeb.py

# Run specific test
python -m unittest tests.test_kgeb.TestEntityExtraction

# Verbose output
python tests/test_kgeb.py -v

# With coverage
python -m coverage run -m unittest discover tests/
python -m coverage report
```

---

## ⚙️ Configuration

### Add Custom Entity Type

1. Update `config/entities.json`:
```json
{
  "CustomEntity": ["attr1", "attr2", "attr3"]
}
```

2. Add extraction method to `EntityExtractor`:
```python
def extract_custom_entities(self, text):
    # Implementation
    pass
```

3. Update `extract_all()`:
```python
"CustomEntity": self.extract_custom_entities(text),
```

### Add Custom Relation Type

1. Update `config/relations.json` with new relation type
2. Add extraction method to `RelationExtractor`
3. Update `extract_all()` to include new method

See CONFIGURATION_GUIDE.md for detailed examples.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Python not found | Install Python 3.8+ and add to PATH |
| Module not found | Run `setup.bat` (Windows) or `bash setup.sh` (Linux/macOS) |
| Output directory missing | Create `output/` folder or run setup script |
| Low extraction accuracy | Refine regex patterns in extractor methods |
| Memory issues | Use batch processing or reduce chunk size |

---

## 📈 Metrics Explained

| Metric | Formula | Range | Interpretation |
|--------|---------|-------|-----------------|
| **Precision** | TP/(TP+FP) | 0-100% | Accuracy of predictions |
| **Recall** | TP/(TP+FN) | 0-100% | Coverage of actual items |
| **F1 Score** | 2×(P×R)/(P+R) | 0-100% | Harmonic mean of P and R |
| **Schema Compliance** | Compliant Attrs/Total Attrs | 0-100% | % of complete entities |
| **Logical Consistency** | Valid Relations/Total | 0-100% | % of valid entity refs |

---

## 🎓 Learning Resources

- **Setup**: See README.md
- **Configuration**: See CONFIGURATION_GUIDE.md
- **Testing**: See TEST_REPORT_TEMPLATE.md
- **Navigation**: See PROJECT_INDEX.md
- **Code**: Check src/ directory

---

## 📞 Common Tasks

### Process Multiple Documents
```bash
for file in data/*.txt; do
  python src/pipeline.py "$file" "$(basename $file)"
done
```

### Compare Methods
```bash
# Run multiple extraction methods and compare reports
python src/pipeline.py data/documents.txt "Method-1"
python src/pipeline.py data/documents.txt "Method-2"
# Compare output/evaluation_report.json files
```

### Custom Extraction
```python
# Create custom extraction pipeline
from src.pipeline import KGEBPipeline

pipeline = KGEBPipeline()
entities, relations, _, _ = pipeline.run_extraction('input.txt')
# Process entities and relations
```

---

## ✅ Pre-Deployment Checklist

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python tests/test_kgeb.py`)
- [ ] Configuration validated (`config/entities.json` and `config/relations.json`)
- [ ] Sample extraction works (`python src/pipeline.py data/documents.txt`)
- [ ] Output files generated correctly
- [ ] Evaluation metrics make sense
- [ ] Documentation reviewed

---

## 🚢 Deployment Options

### Standalone
```bash
python src/pipeline.py documents.txt
```

### Docker
```bash
docker build -t kgeb .
docker run -v $(pwd)/output:/app/output kgeb
```

### API Server (Flask)
```python
from flask import Flask, request
from src.pipeline import KGEBPipeline

app = Flask(__name__)
pipeline = KGEBPipeline()

@app.route('/extract', methods=['POST'])
def extract():
    text = request.json['text']
    report = pipeline.run_full_pipeline(text)
    return report
```

### Batch Processing
```python
# Process multiple documents
documents = ['doc1.txt', 'doc2.txt', 'doc3.txt']
for doc in documents:
    pipeline.run_full_pipeline(doc)
```

---

## 📝 Notes

- KGEB uses pattern matching (regex) for extraction
- For better accuracy, consider ML/NLP models for production
- Schema compliance checks only required attributes
- Logical consistency validates entity references
- All output is in standard JSON format
- Results are reproducible given same input and configuration

---

**Quick Reference Version**: 1.0  
**Last Updated**: November 25, 2025  
**Status**: ✅ Ready to Use
