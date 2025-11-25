# KGEB - Enterprise Knowledge Graph Extraction Benchmark

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Overview

**KGEB** is an enterprise knowledge graph extraction benchmark framework designed to evaluate AI methods on entity recognition and relation extraction from semi-structured enterprise text. It provides a reproducible, standardized evaluation framework for knowledge graph construction pipelines.

### Key Features

- ✅ **10 Entity Types** with comprehensive attributes
- ✅ **30 Relation Types** capturing enterprise relationships
- ✅ **Automated Extraction Pipeline** using NLP pattern matching
- ✅ **Comprehensive Evaluation Framework** with multiple metrics
- ✅ **Reproducible Environment Setup** with Docker support
- ✅ **Automated Test Suite** for validation
- ✅ **Detailed Reporting** with structured outputs

## 🎯 Objectives

### 1. Entity Extraction Task
Identify and extract 10 entity types from semi-structured enterprise text:
- **Person**: name, age, position, department
- **Company**: name, industry, sector, location
- **Project**: name, start_date, end_date, status, budget
- **Department**: name, head, employee_count
- **Position**: title, level, salary_range
- **Technology**: name, category, version
- **Location**: city, country, office_type
- **Team**: name, size, focus_area
- **Product**: name, version, release_date
- **Client**: name, contract_value, industry

### 2. Relation Extraction Task
Identify relationships between entities (30 relation types):
- **WorksAt**: Person → Company
- **ManagesProject**: Person → Project
- **OwnsProject**: Company → Project
- **UsesTechnology**: Team/Project → Technology
- **BelongsTo**: Person → Department
- **Contributes**: Person → Project
- And 24 more relation types...

### 3. Evaluation Framework
Evaluate extraction quality using:
- **Precision, Recall, F1 Score**: Standard metrics for each entity/relation type
- **Schema Compliance**: % of entities with complete attributes
- **Logical Consistency**: % of relations with valid entity references
- **Method Comparison**: Standardized reporting for different extraction methods

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start

#### Linux/macOS
```bash
# Clone or navigate to project
cd kgeb

# Setup environment
bash setup.sh

# Run pipeline
bash run_test.sh documents.txt
```

#### Windows
```cmd
cd kgeb

# Setup environment
setup.bat

# Run pipeline
run_test.bat documents.txt
```

### Docker Setup
```bash
# Build Docker image
docker build -t kgeb:latest .

# Run container
docker run -v $(pwd)/output:/app/output kgeb:latest
```

## 🚀 Usage

### Running the Complete Pipeline

```bash
python src/pipeline.py documents.txt "My Extraction Method"
```

**Output:**
- `output/entities_output.json` - Extracted entities
- `output/relations_output.json` - Extracted relations
- `output/evaluation_report.json` - Evaluation metrics and scores

### Individual Components

#### Entity Extraction
```bash
python src/entity_extractor.py documents.txt entities_output.json
```

#### Relation Extraction
```bash
python src/relation_extractor.py documents.txt relations_output.json
```

#### Evaluation
```bash
python src/evaluator.py entities_output.json relations_output.json evaluation_report.json
```

### Running Tests
```bash
python tests/test_kgeb.py
```

## 📊 Output Formats

### Entities Output (`entities_output.json`)
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
      "location": null
    }
  ],
  "Project": [
    {
      "name": "Alpha",
      "start_date": "2023-01-15",
      "end_date": "2023-06-30",
      "status": "Completed",
      "budget": null
    }
  ]
}
```

### Relations Output (`relations_output.json`)
```json
{
  "WorksAt": [
    {
      "person": "John Doe",
      "company": "OpenAI",
      "employment_type": "Full-time"
    }
  ],
  "ManagesProject": [
    {
      "person": "John Doe",
      "project": "Alpha",
      "role": "Manager"
    }
  ],
  "UsesTechnology": [
    {
      "entity": "AI R&D Team",
      "technology": "Deep Learning Platform",
      "adoption_date": "2024-01-01"
    }
  ]
}
```

### Evaluation Report (`evaluation_report.json`)
```json
{
  "method": "KGEB Pipeline",
  "timestamp": "2025-11-25T12:30:00Z",
  "entity_evaluation": {
    "schema_compliance": {
      "percentage": 95.5,
      "details": {}
    },
    "entity_f1": 0.85
  },
  "relation_evaluation": {
    "logical_consistency": {
      "score": 0.92,
      "issues": []
    },
    "relation_f1": 0.78
  },
  "overall_metrics": {
    "entity_f1": 0.85,
    "relation_f1": 0.78,
    "schema_compliance": 95.5,
    "logical_consistency": 92.0
  }
}
```

## 🧪 Test Suite

The KGEB test suite includes:

### Entity Extraction Tests
- ✅ Person entity extraction
- ✅ Company entity extraction
- ✅ Project entity extraction with date validation
- ✅ JSON serialization

### Relation Extraction Tests
- ✅ WorksAt relation extraction
- ✅ ManagesProject relation extraction
- ✅ OwnsProject relation inference

### Evaluation Tests
- ✅ Precision/Recall/F1 calculation
- ✅ Schema compliance checking
- ✅ Logical consistency validation

### Integration Tests
- ✅ End-to-end pipeline execution
- ✅ Multi-document processing
- ✅ Conflict handling

### Persistence Tests
- ✅ File I/O operations
- ✅ JSON serialization

Run all tests:
```bash
python tests/test_kgeb.py -v
```

## 📈 Evaluation Metrics

### Precision
Fraction of predicted items that are correct:
```
Precision = TP / (TP + FP)
```

### Recall
Fraction of ground truth items that are predicted:
```
Recall = TP / (TP + FN)
```

### F1 Score
Harmonic mean of precision and recall:
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

### Schema Compliance
Percentage of entities with all required attributes:
```
Compliance = (Compliant Attributes / Total Expected Attributes) * 100
```

### Logical Consistency
Percentage of relations with valid entity references:
```
Consistency = 1 - (Invalid Relations / Total Relations)
```

## 🏗️ Project Structure

```
kgeb/
├── src/                           # Core source code
│   ├── entity_extractor.py        # Entity extraction module
│   ├── relation_extractor.py      # Relation extraction module
│   ├── evaluator.py               # Evaluation framework
│   └── pipeline.py                # Main pipeline orchestrator
├── tests/
│   └── test_kgeb.py               # Comprehensive test suite
├── config/
│   ├── entities.json              # Entity schema definitions
│   └── relations.json             # Relation type definitions
├── data/                          # Input documents
│   └── documents.txt              # Sample enterprise text
├── output/                        # Generated outputs
│   ├── entities_output.json       # Extracted entities
│   ├── relations_output.json      # Extracted relations
│   └── evaluation_report.json     # Evaluation results
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image definition
├── setup.sh / setup.bat           # Environment setup scripts
├── run_test.sh / run_test.bat     # Pipeline execution scripts
└── README.md                      # This file
```

## 🔧 Configuration

### Entity Schema (`config/entities.json`)
Defines 10 entity types and their attributes. Modify to customize entity types.

### Relation Schema (`config/relations.json`)
Defines 30 relation types with source/target entity mappings. Extend to add new relation types.

## 🤝 Real-World Scenarios

### Multi-Document Processing
Process multiple documents sequentially:
```bash
for doc in data/*.txt; do
  python src/pipeline.py "$doc" "$(basename $doc)"
done
```

### Batch Evaluation
Compare multiple extraction methods:
```bash
python src/evaluator.py entities1.json relations1.json report1.json
python src/evaluator.py entities2.json relations2.json report2.json
```

### Custom Entity Types
Add custom entities by updating `config/entities.json` and extending `EntityExtractor` class.

## 📋 Test Report Template

Detailed test results include:

1. **Entity Extraction Results**
   - Count of extracted entities by type
   - Schema compliance percentage
   - F1 scores by entity type

2. **Relation Extraction Results**
   - Count of extracted relations by type
   - Logical consistency score
   - F1 scores by relation type

3. **Overall Metrics**
   - Average entity F1
   - Average relation F1
   - Overall schema compliance
   - Overall logical consistency

4. **Issues and Recommendations**
   - Invalid entity references
   - Incomplete attribute coverage
   - Suggestions for improvement

## 🚀 Advanced Usage

### Custom Entity Extractor
```python
from entity_extractor import EntityExtractor

# Load schema
schema = {
    "CustomEntity": ["attr1", "attr2", "attr3"]
}

# Create extractor
extractor = EntityExtractor(schema)

# Extract from text
text = "Your enterprise text here..."
entities = extractor.extract_all(text)

# Save results
extractor.save_to_file("output.json")
```

### Custom Evaluator
```python
from evaluator import Evaluator

# Create evaluator
evaluator = Evaluator(entities_schema, relations_schema)

# Evaluate with ground truth
report = evaluator.generate_report(
    entity_results,
    relation_results,
    method_name="Custom Method"
)

# Save report
evaluator.save_report(report, "report.json")
```

## 📝 API Reference

### EntityExtractor
- `extract_persons(text)` - Extract Person entities
- `extract_companies(text)` - Extract Company entities
- `extract_projects(text)` - Extract Project entities
- `extract_all(text)` - Extract all entity types
- `save_to_file(filepath)` - Save entities to JSON

### RelationExtractor
- `extract_works_at(text)` - Extract WorksAt relations
- `extract_manages_project(text)` - Extract ManagesProject relations
- `extract_all(text)` - Extract all relation types
- `save_to_file(filepath)` - Save relations to JSON

### Evaluator
- `evaluate_entities(extracted_entities, ground_truth)` - Evaluate entities
- `evaluate_relations(extracted_relations, entities, ground_truth)` - Evaluate relations
- `generate_report(entity_results, relation_results)` - Generate evaluation report
- `save_report(report, filepath)` - Save report to JSON

## ❓ FAQ

**Q: Can I use KGEB with my own data?**
A: Yes! Place your documents in the `data/` directory and run the pipeline with your document path.

**Q: How do I add custom relation types?**
A: Update `config/relations.json` and extend the `RelationExtractor` class with custom extraction methods.

**Q: Can I use KGEB with other extraction methods?**
A: Yes! The evaluation framework works independently of the extraction method. Just provide entities and relations in the standard JSON format.

**Q: What's the performance overhead?**
A: Extraction and evaluation on 100+ records typically completes in < 1 second on modern hardware.

**Q: Can I run KGEB in Docker?**
A: Yes! Use the provided `Dockerfile` for containerized deployment.

## 🐛 Troubleshooting

### Issue: Python not found
**Solution**: Install Python 3.8+ and ensure it's in your PATH.

### Issue: Module not found errors
**Solution**: Run `setup.sh` (Linux/macOS) or `setup.bat` (Windows) to install dependencies.

### Issue: Invalid date format in projects
**Solution**: Check that dates follow YYYY-MM-DD format. Invalid dates are skipped automatically.

### Issue: Missing output files
**Solution**: Ensure the `output/` directory exists and has write permissions.

## 📚 Further Reading

- [Enterprise Knowledge Graph Construction](https://example.com)
- [Named Entity Recognition Best Practices](https://example.com)
- [Relation Extraction Evaluation](https://example.com)
- [Knowledge Graph Applications](https://example.com)

## 📄 License

KGEB is released under the MIT License. See LICENSE file for details.

## 🙏 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check the FAQ section

## 🎓 Citation

If you use KGEB in your research, please cite:

```bibtex
@software{kgeb2025,
  title={KGEB: Enterprise Knowledge Graph Extraction Benchmark},
  author={Your Organization},
  year={2025},
  url={https://github.com/yourorg/kgeb}
}
```

---

**Version**: 1.0.0  
**Last Updated**: November 25, 2025  
**Maintainer**: KGEB Team
