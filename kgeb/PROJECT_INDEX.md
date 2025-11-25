# KGEB Project Index

## 📚 Quick Navigation

Welcome to the KGEB (Enterprise Knowledge Graph Extraction Benchmark) project. This index provides quick access to all documentation and files.

---

## 🚀 Getting Started

| Document | Purpose | Time |
|----------|---------|------|
| [README.md](README.md) | Project overview and quick start | 5 min |
| [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) | Configuration and customization | 15 min |
| [TEST_REPORT_TEMPLATE.md](TEST_REPORT_TEMPLATE.md) | Test report format and examples | 10 min |

---

## 📁 Project Structure

```
kgeb/
├── src/                          # Core implementation
│   ├── entity_extractor.py       # Entity extraction engine
│   ├── relation_extractor.py     # Relation extraction engine
│   ├── evaluator.py              # Evaluation framework
│   └── pipeline.py               # Main orchestrator
│
├── tests/
│   └── test_kgeb.py              # Comprehensive test suite
│
├── config/                       # Configuration files
│   ├── entities.json             # Entity type definitions
│   └── relations.json            # Relation type definitions
│
├── output/                       # Generated outputs
│   ├── entities_output.json      # Extracted entities
│   ├── relations_output.json     # Extracted relations
│   └── evaluation_report.json    # Evaluation results
│
├── data/                         # Input documents
│   └── documents.txt             # Sample enterprise text
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
├── setup.sh / setup.bat          # Environment setup
├── run_test.sh / run_test.bat    # Pipeline execution
├── README.md                     # Main documentation
├── CONFIGURATION_GUIDE.md        # Configuration guide
├── TEST_REPORT_TEMPLATE.md       # Report template
└── PROJECT_INDEX.md              # This file
```

---

## 🔧 Core Modules

### Entity Extractor (`src/entity_extractor.py`)

Extracts 10 entity types from semi-structured text:

**Key Classes:**
- `EntityExtractor` - Main extraction class

**Key Methods:**
- `extract_persons()` - Extract Person entities
- `extract_companies()` - Extract Company entities
- `extract_projects()` - Extract Project entities
- `extract_all()` - Extract all entity types
- `save_to_file()` - Save to JSON

**Usage:**
```python
from entity_extractor import EntityExtractor

extractor = EntityExtractor(schema)
entities = extractor.extract_all(text)
extractor.save_to_file('entities.json')
```

### Relation Extractor (`src/relation_extractor.py`)

Extracts 30 relation types between entities:

**Key Classes:**
- `RelationExtractor` - Main extraction class

**Key Methods:**
- `extract_works_at()` - Person → Company
- `extract_manages_project()` - Person → Project
- `extract_owns_project()` - Company → Project
- `extract_all()` - Extract all relation types
- `save_to_file()` - Save to JSON

**Usage:**
```python
from relation_extractor import RelationExtractor

extractor = RelationExtractor(schema, entities)
relations = extractor.extract_all(text)
extractor.save_to_file('relations.json')
```

### Evaluator (`src/evaluator.py`)

Evaluates extraction quality:

**Key Classes:**
- `EvaluationMetrics` - Static metrics calculation
- `Evaluator` - Main evaluation class

**Key Methods:**
- `calculate_precision_recall_f1()` - Calculate standard metrics
- `check_schema_compliance()` - Verify schema compliance
- `check_logical_consistency()` - Check entity references
- `evaluate_entities()` - Evaluate entities
- `evaluate_relations()` - Evaluate relations
- `generate_report()` - Create evaluation report
- `save_report()` - Save report to JSON

**Usage:**
```python
from evaluator import Evaluator

evaluator = Evaluator(entities_schema, relations_schema)
entity_results = evaluator.evaluate_entities(entities)
relation_results = evaluator.evaluate_relations(relations, entities)
report = evaluator.generate_report(entity_results, relation_results)
evaluator.save_report(report, 'report.json')
```

### Pipeline (`src/pipeline.py`)

Orchestrates the complete extraction and evaluation workflow:

**Key Classes:**
- `KGEBPipeline` - Main pipeline orchestrator

**Key Methods:**
- `load_schemas()` - Load entity and relation schemas
- `run_extraction()` - Execute extraction phase
- `run_evaluation()` - Execute evaluation phase
- `run_full_pipeline()` - Execute complete pipeline

**Usage:**
```bash
python src/pipeline.py documents.txt "Method Name"
```

---

## 🧪 Test Suite (`tests/test_kgeb.py`)

Comprehensive test coverage including:

| Test Class | Tests | Coverage |
|-----------|-------|----------|
| TestEntityExtraction | 6 tests | Person, Company, Project extraction; date validation |
| TestRelationExtraction | 3 tests | WorksAt, ManagesProject, OwnsProject relations |
| TestEvaluationMetrics | 5 tests | Precision/Recall/F1, schema compliance, consistency |
| TestEvaluator | 3 tests | Entity evaluation, relation evaluation, report generation |
| TestPersistence | 2 tests | File I/O, JSON serialization |
| TestRealWorldScenarios | 2 tests | Multi-document, conflict handling |
| TestIntegration | 1 test | End-to-end pipeline |

**Run Tests:**
```bash
python tests/test_kgeb.py                    # Run all tests
python tests/test_kgeb.py -v                 # Verbose output
python -m unittest tests.test_kgeb.TestEntityExtraction  # Run specific test
```

---

## ⚙️ Configuration Files

### Entity Schema (`config/entities.json`)

Defines 10 entity types and their attributes:

```json
{
  "Person": ["name", "age", "position", "department"],
  "Company": ["name", "industry", "sector", "location"],
  "Project": ["name", "start_date", "end_date", "status", "budget"],
  "Department": ["name", "head", "employee_count"],
  "Position": ["title", "level", "salary_range"],
  "Technology": ["name", "category", "version"],
  "Location": ["city", "country", "office_type"],
  "Team": ["name", "size", "focus_area"],
  "Product": ["name", "version", "release_date"],
  "Client": ["name", "contract_value", "industry"]
}
```

### Relation Schema (`config/relations.json`)

Defines 30 relation types with metadata:

```json
{
  "relation_types": [
    {
      "id": 1,
      "name": "BelongsTo",
      "source_entity": "Person",
      "target_entity": "Department",
      "attributes": ["start_date", "role"]
    },
    // ... 29 more relation types
  ]
}
```

---

## 📊 Output Formats

### Entities Output

```json
{
  "Person": [{"name": "...", "age": 0, "position": "...", "department": "..."}],
  "Company": [{"name": "...", "industry": "...", "sector": "...", "location": "..."}],
  // ... other entity types
}
```

### Relations Output

```json
{
  "WorksAt": [{"person": "...", "company": "...", "employment_type": "..."}],
  "ManagesProject": [{"person": "...", "project": "...", "role": "..."}],
  // ... other relation types
}
```

### Evaluation Report

```json
{
  "method": "...",
  "timestamp": "...",
  "overall_metrics": {
    "entity_f1": 0.85,
    "relation_f1": 0.78,
    "schema_compliance": 95.5,
    "logical_consistency": 92.0
  }
}
```

---

## 📋 Setup Instructions

### Linux/macOS

```bash
cd kgeb
bash setup.sh              # Setup environment
bash run_test.sh           # Run pipeline
```

### Windows

```cmd
cd kgeb
setup.bat                  # Setup environment
run_test.bat               # Run pipeline
```

### Docker

```bash
docker build -t kgeb:latest .
docker run -v $(pwd)/output:/app/output kgeb:latest
```

---

## 📈 Workflow

```
┌─────────────────────────────────────────────────────────┐
│ Input: documents.txt (100+ enterprise records)          │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼───────────┐       ┌────────▼─────────┐
│ Entity Extraction │       │ Relation         │
│                   │       │ Extraction       │
│ - Person (52)     │       │                  │
│ - Company (10)    │       │ - WorksAt (52)   │
│ - Project (28)    │       │ - ManagesProject │
│ - ... (others)    │       │   (30)           │
└───────┬───────────┘       └────────┬─────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
            ┌──────────▼──────────┐
            │ Evaluation          │
            │                     │
            │ - Precision: 85%    │
            │ - Recall: 82%       │
            │ - F1: 83.5%         │
            │ - Compliance: 95%   │
            │ - Consistency: 92%  │
            └──────────┬──────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼──────────────┐   ┌─────────▼────────────┐
│ entities_output.json │   │ relations_output.json│
└──────────────────────┘   └─────────────────────┘
                      │
            ┌─────────▼─────────┐
            │ evaluation_report │
            │ .json             │
            └───────────────────┘
```

---

## 🔍 Quick Reference

### Common Commands

```bash
# Setup
python src/pipeline.py documents.txt

# Run tests
python tests/test_kgeb.py

# Specific extraction
python src/entity_extractor.py input.txt output.json
python src/relation_extractor.py input.txt output.json
python src/evaluator.py entities.json relations.json report.json

# With Docker
docker build -t kgeb .
docker run -v $(pwd)/output:/app/output kgeb
```

### API Usage

```python
from src.entity_extractor import EntityExtractor
from src.relation_extractor import RelationExtractor
from src.evaluator import Evaluator

# Extract entities
entities = EntityExtractor(schema).extract_all(text)

# Extract relations
relations = RelationExtractor(schema, entities).extract_all(text)

# Evaluate
evaluator = Evaluator(schema, relations_schema)
report = evaluator.generate_report(entity_results, relation_results)
```

---

## 📚 Documentation Map

| Topic | Files |
|-------|-------|
| **Setup & Quick Start** | README.md |
| **Configuration & Customization** | CONFIGURATION_GUIDE.md |
| **Testing & Validation** | test_kgeb.py, TEST_REPORT_TEMPLATE.md |
| **Core Implementation** | entity_extractor.py, relation_extractor.py, evaluator.py |
| **Deployment** | Dockerfile, setup.sh, setup.bat |
| **Execution** | pipeline.py, run_test.sh, run_test.bat |

---

## ❓ FAQ

**Q: Where do I place my input documents?**
A: Place documents in the `data/` directory or specify the path in the pipeline command.

**Q: Can I add custom entity types?**
A: Yes! See CONFIGURATION_GUIDE.md for detailed instructions.

**Q: How do I integrate KGEB into my system?**
A: Use the pipeline.py module or Docker container for integration.

**Q: What's the typical performance?**
A: ~1-2 seconds for 100 records on modern hardware.

---

## 🔗 Related Resources

- [Named Entity Recognition](https://example.com)
- [Relation Extraction Methods](https://example.com)
- [Knowledge Graph Construction](https://example.com)
- [Evaluation Metrics](https://example.com)

---

## 📞 Support & Contact

- **Documentation**: See README.md
- **Configuration**: See CONFIGURATION_GUIDE.md
- **Issues**: Check test_kgeb.py for error patterns
- **Customization**: See CONFIGURATION_GUIDE.md

---

**Project Version**: 1.0.0  
**Last Updated**: November 25, 2025  
**Status**: ✅ Production Ready
