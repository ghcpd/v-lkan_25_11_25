# Enterprise Knowledge Graph Extraction Benchmark (KGEB)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> A reproducible framework for evaluating AI methods on entity recognition and relation extraction from semi-structured enterprise text.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Entity Types](#entity-types)
- [Relation Types](#relation-types)
- [Evaluation Metrics](#evaluation-metrics)
- [Testing](#testing)
- [Docker Support](#docker-support)
- [Contributing](#contributing)

## 🎯 Overview

KGEB (Enterprise Knowledge Graph Extraction Benchmark) is an open-source framework designed to evaluate AI methods on extracting structured knowledge from enterprise documents. It provides:

- **10 Entity Types** with comprehensive attributes
- **30 Relation Types** between entities
- **Robust Evaluation Framework** with precision, recall, F1 metrics
- **Schema Compliance Validation**
- **Logical Consistency Checking**
- **Reproducible Testing Environment**

## ✨ Features

### Entity Extraction
- Extract 10 types of entities: Person, Company, Project, Department, Position, Technology, Location, Team, Product, Client
- Each entity type has 3-4 mandatory attributes
- Schema validation and compliance checking
- Automatic deduplication

### Relation Extraction
- Identify 30 types of relations between entities
- Support for complex multi-entity relationships
- Attribute-rich relations with metadata
- Cross-entity consistency validation

### Evaluation Framework
- **Performance Metrics**: Precision, Recall, F1 Score (overall and per-type)
- **Schema Compliance**: Validates against predefined entity/relation schemas
- **Logical Consistency**: Checks referential integrity between entities and relations
- **Attribute Completeness**: Measures completeness of extracted attributes

### Reproducibility
- Docker container for consistent environment
- Automated setup scripts
- Comprehensive test suite
- Version-controlled schemas

## 📁 Project Structure

```
KGEB/
├── documents.txt              # Input: Semi-structured enterprise documents
├── entities.json              # Schema: 10 entity type definitions
├── relations.json             # Schema: 30 relation type definitions
│
├── entity_extractor.py        # Module: Entity extraction logic
├── relation_extractor.py      # Module: Relation extraction logic
├── evaluator.py               # Module: Evaluation framework
├── main.py                    # CLI: Command-line interface
│
├── test_kgeb.py              # Tests: Comprehensive test suite
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker configuration
├── setup.sh                   # Setup script (Linux/Mac)
│
├── run_pipeline.sh            # Pipeline runner (Linux/Mac)
├── run_pipeline.bat           # Pipeline runner (Windows)
├── run_test.sh                # Test runner (Linux/Mac)
├── run_test.bat               # Test runner (Windows)
├── quick_start.sh             # One-click setup and run
│
├── output/                    # Generated outputs
│   ├── entities_output.json
│   ├── relations_output.json
│   └── evaluation_report.json
│
├── logs/                      # Execution logs
└── test_results/              # Test reports and coverage
```

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Git

### Method 1: Local Installation

```bash
# Clone the repository
git clone <repository-url>
cd KGEB

# Run setup script
bash setup.sh

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate      # Windows
```

### Method 2: Docker Installation

```bash
# Build Docker image
docker build -t kgeb:latest .

# Run container
docker run -it kgeb:latest
```

## ⚡ Quick Start

### One-Click Execution (Linux/Mac)

```bash
bash quick_start.sh
```

### Manual Execution

```bash
# 1. Extract entities
python main.py extract-entities --documents documents.txt

# 2. Extract relations
python main.py extract-relations --documents documents.txt

# 3. Evaluate results
python main.py evaluate

# Or run the complete pipeline
python main.py run
```

### Using Shell Scripts

```bash
# Run full pipeline
bash run_pipeline.sh

# Or on Windows
run_pipeline.bat
```

## 💻 Usage

### Command-Line Interface

KGEB provides a comprehensive CLI with the following commands:

#### 1. Run Full Pipeline

```bash
python main.py run [OPTIONS]

Options:
  -d, --documents TEXT    Path to documents file (default: documents.txt)
  -m, --method TEXT       Method name (default: KGEB Baseline)
  -o, --output-dir TEXT   Output directory (default: output)
```

#### 2. Extract Entities

```bash
python main.py extract-entities [OPTIONS]

Options:
  -d, --documents TEXT       Path to documents file
  -e, --entities-schema TEXT Path to entities schema
  -o, --output TEXT          Path to output file
```

#### 3. Extract Relations

```bash
python main.py extract-relations [OPTIONS]

Options:
  -d, --documents TEXT        Path to documents file
  -e, --entities TEXT         Path to entities file
  -r, --relations-schema TEXT Path to relations schema
  -o, --output TEXT           Path to output file
```

#### 4. Evaluate Results

```bash
python main.py evaluate [OPTIONS]

Options:
  -m, --method TEXT             Method name
  -e, --entities-predicted TEXT Path to predicted entities
  -r, --relations-predicted TEXT Path to predicted relations
  --entities-gt TEXT            Path to ground truth entities (optional)
  --relations-gt TEXT           Path to ground truth relations (optional)
  -o, --output TEXT             Path to output report
```

#### 5. Run Tests

```bash
python main.py test [-v]
```

#### 6. Display Statistics

```bash
python main.py stats [OPTIONS]

Options:
  -e, --entities TEXT   Path to entities file
  -r, --relations TEXT  Path to relations file
```

#### 7. Show Information

```bash
python main.py info
```

### Programmatic API

```python
from entity_extractor import EntityExtractor
from relation_extractor import RelationExtractor
from evaluator import KGEBEvaluator

# Extract entities
extractor = EntityExtractor("entities.json")
entities = extractor.extract_from_file("documents.txt")
extractor.save_to_json("output/entities_output.json")

# Extract relations
rel_extractor = RelationExtractor("relations.json")
rel_extractor.load_entities("output/entities_output.json")
relations = rel_extractor.extract_from_file("documents.txt")
rel_extractor.save_to_json("output/relations_output.json")

# Evaluate
evaluator = KGEBEvaluator()
report = evaluator.generate_report(
    method_name="My Method",
    entities_predicted="output/entities_output.json",
    relations_predicted="output/relations_output.json"
)
evaluator.print_summary(report)
```

## 📊 Entity Types

KGEB extracts **10 entity types**, each with specific attributes:

| Entity Type | Attributes |
|-------------|-----------|
| **Person** | name, age, position, department |
| **Company** | name, industry, sector, location |
| **Project** | name, start_date, end_date, status, budget |
| **Department** | name, head, employee_count |
| **Position** | title, level, salary_range |
| **Technology** | name, category, version |
| **Location** | city, country, office_type |
| **Team** | name, size, focus_area |
| **Product** | name, version, release_date |
| **Client** | name, contract_value, industry |

### Example Entity Output

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

## 🔗 Relation Types

KGEB identifies **30 relation types** between entities:

### Person Relations
1. **WorksAt**: Person works at Company
2. **BelongsToDepartment**: Person belongs to Department
3. **ManagesProject**: Person manages Project
4. **LeadsTeam**: Person leads Team
5. **HasPosition**: Person has Position
6. **LocatedIn**: Person located in Location

### Company Relations
7. **CompanyOwnsProject**: Company owns Project
8. **CompanyHasDepartment**: Company has Department
9. **CompanyLocatedIn**: Company located in Location
10. **CompanyHasClient**: Company has Client
11. **CompanyDevelopsProduct**: Company develops Product
12. **CompanyUsesTechnology**: Company uses Technology
13. **CompanyPartnersWith**: Company partners with Company

### Project Relations
14. **ProjectUsesTechnology**: Project uses Technology
15. **ProjectHasTeam**: Project has Team
16. **ProjectForClient**: Project for Client
17. **ProjectDeliversProduct**: Project delivers Product

### Department Relations
18. **DepartmentHeadedBy**: Department headed by Person
19. **DepartmentHasTeam**: Department has Team
20. **DepartmentLocatedIn**: Department located in Location

### Other Relations
21. **PositionInDepartment**: Position in Department
22. **TeamMember**: Team has member Person
23. **TeamUsesTechnology**: Team uses Technology
24. **TeamDevelopsProduct**: Team develops Product
25. **ProductUsesTechnology**: Product uses Technology
26. **ProductForClient**: Product for Client
27. **ClientInLocation**: Client in Location
28. **ClientHasContract**: Client has contract with Company
29. **TechnologyCategory**: Technology belongs to category
30. **LocationContainsLocation**: Location contains Location

### Example Relation Output

```json
{
  "WorksAt": [
    {
      "person": "John Doe",
      "company": "OpenAI",
      "position": "Researcher",
      "start_date": "2020-01-01"
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

## 📈 Evaluation Metrics

### Performance Metrics

- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)

Calculated both **overall** and **per entity/relation type**.

### Schema Compliance

- **Coverage**: Percentage of expected types extracted
- **Attribute Completeness**: Percentage of entities/relations with all required attributes
- **Issue Reporting**: Details on missing or extra attributes

### Logical Consistency

- **Referential Integrity**: Ensures relations reference existing entities
- **Cross-validation**: Checks for contradictions between relations
- **Consistency Score**: Overall consistency rating

### Example Evaluation Report

```json
{
  "method": "KGEB Baseline Method",
  "timestamp": "2025-11-25T10:30:00Z",
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
    "f1_score": 0.78,
    "precision": 0.81,
    "recall": 0.75,
    "logical_consistency": {
      "consistent": true,
      "issues": []
    }
  }
}
```

## 🧪 Testing

KGEB includes a comprehensive test suite covering all components.

### Run Tests

```bash
# Using Python
python main.py test

# Using pytest directly
pytest test_kgeb.py -v

# Using shell script (with coverage)
bash run_test.sh
# or on Windows
run_test.bat
```

### Test Coverage

The test suite includes:

- **Unit Tests**: For individual functions in each module
- **Integration Tests**: For the complete pipeline
- **Entity Extraction Tests**: Validates entity extraction accuracy
- **Relation Extraction Tests**: Validates relation extraction accuracy
- **Evaluation Tests**: Tests evaluation metrics and reporting
- **Edge Case Tests**: Handles malformed data, missing files, etc.

### Coverage Report

After running tests, view the coverage report:

```bash
# Open HTML coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🐳 Docker Support

### Build Docker Image

```bash
docker build -t kgeb:latest .
```

### Run in Docker

```bash
# Run full pipeline
docker run -v $(pwd)/output:/app/output kgeb:latest python main.py run

# Run tests
docker run kgeb:latest python main.py test

# Interactive shell
docker run -it kgeb:latest /bin/bash
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  kgeb:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    command: python main.py run
```

Run with:
```bash
docker-compose up
```

## 📝 Example Workflow

### 1. Prepare Your Data

Place your enterprise documents in `documents.txt`:

```text
John Doe, age 32, works at OpenAI as a Researcher.
Jane Smith, age 28, works at Google as an Engineer.

John Doe manages 3 projects: Alpha, Beta, Gamma.
...
```

### 2. Run Extraction

```bash
python main.py run --method "My Method v1.0"
```

### 3. Review Results

```bash
# View statistics
python main.py stats

# Check entities
cat output/entities_output.json

# Check relations
cat output/relations_output.json

# Review evaluation
cat output/evaluation_report.json
```

### 4. Compare Methods

```bash
# Run method A
python main.py run --method "Method A" --output-dir output/method_a

# Run method B
python main.py run --method "Method B" --output-dir output/method_b

# Compare reports
diff output/method_a/evaluation_report.json output/method_b/evaluation_report.json
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run code formatter
black *.py

# Run linter
flake8 *.py

# Run tests
pytest test_kgeb.py -v
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- transformers for advanced language models
- pytest for testing framework
- All contributors to this project

---

**Happy Knowledge Graph Extracting! 🚀**