# KGEB Development Guide

## Getting Started

This guide helps you set up a development environment for KGEB.

## Prerequisites

- Python 3.10+
- Git
- Virtual environment tool

## Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd KGEB

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-html black flake8 mypy
```

## Code Style

### Python Style Guide

We follow PEP 8 with the following specifics:

- Line length: 100 characters
- Use 4 spaces for indentation
- Use type hints where possible

### Formatting

```bash
# Format code with black
black *.py

# Check style with flake8
flake8 *.py --max-line-length=100
```

### Type Checking

```bash
# Run mypy for type checking
mypy entity_extractor.py relation_extractor.py evaluator.py
```

## Testing

### Running Tests

```bash
# Run all tests
pytest test_kgeb.py -v

# Run with coverage
pytest test_kgeb.py --cov=. --cov-report=html

# Run specific test class
pytest test_kgeb.py::TestEntityExtractor -v

# Run specific test
pytest test_kgeb.py::TestEntityExtractor::test_extract_person -v
```

### Writing Tests

All new features should include tests:

```python
def test_new_feature():
    """Test description"""
    # Arrange
    extractor = EntityExtractor()
    
    # Act
    result = extractor.new_feature()
    
    # Assert
    assert result == expected_value
```

## Project Structure

```
KGEB/
├── entity_extractor.py    # Entity extraction logic
├── relation_extractor.py  # Relation extraction logic
├── evaluator.py           # Evaluation framework
├── main.py                # CLI interface
├── test_kgeb.py          # Test suite
└── README.md             # Documentation
```

## Adding New Entity Types

1. Update `entities.json`:
```json
{
  "NewEntity": ["attr1", "attr2", "attr3"]
}
```

2. Add extraction method in `entity_extractor.py`:
```python
def _extract_new_entity(self, line: str):
    # Extraction logic
    pass
```

3. Call method in `extract_from_file()`:
```python
self._extract_new_entity(line)
```

4. Add tests in `test_kgeb.py`:
```python
def test_extract_new_entity(self, extractor):
    # Test logic
    pass
```

## Adding New Relation Types

1. Update `relations.json`:
```json
{
  "name": "NewRelation",
  "source_entity": "Entity1",
  "target_entity": "Entity2",
  "attributes": ["attr1"]
}
```

2. Add extraction method in `relation_extractor.py`:
```python
def _extract_new_relation(self, line: str):
    # Extraction logic
    pass
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Python Debugger

```python
import pdb; pdb.set_trace()
```

### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: KGEB Main",
      "type": "python",
      "request": "launch",
      "program": "main.py",
      "args": ["run"],
      "console": "integratedTerminal"
    }
  ]
}
```

## Performance Optimization

### Profiling

```bash
# Profile execution
python -m cProfile -o profile.stats main.py run

# View results
python -m pstats profile.stats
```

### Memory Profiling

```bash
# Install memory_profiler
pip install memory_profiler

# Profile memory
python -m memory_profiler main.py
```

## Contributing Workflow

1. Create feature branch
2. Make changes
3. Add tests
4. Run tests and style checks
5. Commit changes
6. Push and create PR

## Release Process

1. Update version in `main.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag
5. Build Docker image
6. Push to registry

## Troubleshooting

### Common Issues

**Issue**: spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

**Issue**: Import errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Issue**: Permission denied on scripts
```bash
chmod +x *.sh
```

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [spaCy Documentation](https://spacy.io/usage)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://pep8.org/)

## Questions?

Open an issue on GitHub or contact the maintainers.
