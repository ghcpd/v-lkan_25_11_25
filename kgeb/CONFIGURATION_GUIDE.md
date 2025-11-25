# KGEB Configuration Guide

## Overview

This guide explains how to configure KGEB for different use cases, customize entity and relation types, and optimize performance.

---

## 1. Entity Schema Configuration

### 1.1 Understanding the Current Schema

The default entity schema (`config/entities.json`) defines 10 entity types:

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

### 1.2 Adding Custom Entity Types

To add a new entity type:

1. **Update config/entities.json**:
```json
{
  "CustomEntity": ["attr1", "attr2", "attr3"]
}
```

2. **Add extraction method to EntityExtractor**:
```python
def extract_custom_entities(self, text: str) -> List[Dict[str, Any]]:
    """Extract CustomEntity entities"""
    entities = []
    pattern = r'pattern_to_match'
    matches = re.finditer(pattern, text)
    
    for match in matches:
        entity = {
            "attr1": match.group(1),
            "attr2": match.group(2),
            "attr3": match.group(3)
        }
        entities.append(entity)
    
    return entities
```

3. **Update extract_all method**:
```python
def extract_all(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
    self.extracted_entities = {
        # ... existing entities ...
        "CustomEntity": self.extract_custom_entities(text),
    }
    return self.extracted_entities
```

### 1.3 Modifying Existing Entity Types

To modify an entity type:

1. Update the attribute list in `config/entities.json`
2. Update the corresponding extraction method
3. Update evaluation metrics accordingly

Example - Adding "email" to Person:
```json
{
  "Person": ["name", "age", "position", "department", "email"]
}
```

---

## 2. Relation Schema Configuration

### 2.1 Understanding the Current Schema

The relation schema defines 30 relation types with metadata:

```json
{
  "relation_types": [
    {
      "id": 1,
      "name": "BelongsTo",
      "description": "Person belongs to department",
      "source_entity": "Person",
      "target_entity": "Department",
      "attributes": ["start_date", "role"]
    }
  ]
}
```

### 2.2 Adding Custom Relation Types

To add a new relation type:

1. **Update config/relations.json**:
```json
{
  "id": 31,
  "name": "Mentors",
  "description": "Senior person mentors junior person",
  "source_entity": "Person",
  "target_entity": "Person",
  "attributes": ["duration", "expertise_area"]
}
```

2. **Add extraction method to RelationExtractor**:
```python
def extract_mentors(self, text: str) -> List[Dict[str, Any]]:
    """Extract Mentors relations"""
    relations = []
    pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)\s+mentors?\s+([A-Z][a-z]+ [A-Z][a-z]+)'
    matches = re.finditer(pattern, text)
    
    for match in matches:
        relations.append({
            "mentor": match.group(1),
            "mentee": match.group(2),
            "duration": None,
            "expertise_area": None
        })
    
    return relations
```

3. **Update extract_all method**:
```python
def extract_all(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
    self.extracted_relations = {
        # ... existing relations ...
        "Mentors": self.extract_mentors(text),
    }
    return self.extracted_relations
```

### 2.3 Multi-Entity Relations

For relations with multiple possible source or target entities:

```json
{
  "id": 32,
  "name": "Implements",
  "description": "Team or Person implements technology",
  "source_entity": ["Team", "Person"],
  "target_entity": "Technology",
  "attributes": ["implementation_date", "status"]
}
```

---

## 3. Extraction Pattern Configuration

### 3.1 Regular Expressions

Modify extraction patterns in each extractor method:

```python
# Before
pattern = r'([A-Z][a-z]+ [A-Z][a-z]+),\s*age\s*(\d+)'

# After (more flexible)
pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)[,\s]+age[:\s]*(\d+)'
```

### 3.2 Date Format Handling

Customize date parsing:

```python
def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats"""
    formats = [
        '%Y-%m-%d',      # 2023-01-15
        '%d/%m/%Y',      # 15/01/2023
        '%B %d, %Y',     # January 15, 2023
        '%b %d, %Y',     # Jan 15, 2023
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except ValueError:
            continue
    
    return None
```

### 3.3 Text Preprocessing

Add preprocessing before extraction:

```python
def preprocess_text(text: str) -> str:
    """Preprocess text before extraction"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Normalize punctuation
    text = text.replace('–', '-')  # En-dash to hyphen
    
    # Expand abbreviations
    text = text.replace('Sr.', 'Senior')
    text = text.replace('Jr.', 'Junior')
    
    return text
```

---

## 4. Evaluation Configuration

### 4.1 Custom Metrics

Add custom evaluation metrics:

```python
def calculate_custom_metric(self, entities: Dict) -> float:
    """Calculate custom metric"""
    total = sum(len(items) for items in entities.values())
    complete = sum(
        1 for entity_type, items in entities.items()
        for item in items
        if all(k in item for k in self.schema[entity_type])
    )
    return complete / total if total > 0 else 0.0
```

### 4.2 Metric Weighting

Adjust metric importance:

```python
def generate_weighted_report(self, report: Dict) -> Dict:
    """Generate report with weighted metrics"""
    weights = {
        'entity_f1': 0.40,
        'relation_f1': 0.35,
        'schema_compliance': 0.15,
        'logical_consistency': 0.10
    }
    
    overall_score = sum(
        report['overall_metrics'][metric] * weight
        for metric, weight in weights.items()
    )
    
    report['overall_metrics']['weighted_score'] = overall_score
    return report
```

---

## 5. Performance Optimization

### 5.1 Caching

Add caching for repeated extractions:

```python
from functools import lru_cache

class EntityExtractor:
    @lru_cache(maxsize=128)
    def extract_persons(self, text: str) -> List[Dict[str, Any]]:
        # ... extraction logic ...
```

### 5.2 Parallel Processing

Process documents in parallel:

```python
from concurrent.futures import ProcessPoolExecutor

def process_documents_parallel(documents: List[str]) -> List[Dict]:
    """Process multiple documents in parallel"""
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_single_document, documents))
    return results
```

### 5.3 Incremental Extraction

Process large documents incrementally:

```python
def extract_incremental(self, text: str, chunk_size: int = 1000) -> Dict:
    """Extract entities incrementally from large documents"""
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_entities = {k: [] for k in self.schema}
    
    for chunk in chunks:
        chunk_entities = self.extract_all(chunk)
        for entity_type, items in chunk_entities.items():
            all_entities[entity_type].extend(items)
    
    return all_entities
```

---

## 6. Integration Configuration

### 6.1 Database Integration

Store results in a database:

```python
import sqlite3

def save_to_database(entities: Dict, relations: Dict, db_file: str):
    """Save extraction results to SQLite database"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    for entity_type, items in entities.items():
        cursor.executemany(
            f'INSERT INTO {entity_type} VALUES (?)',
            [json.dumps(item) for item in items]
        )
    
    conn.commit()
    conn.close()
```

### 6.2 API Integration

Expose extraction as an API:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
pipeline = KGEBPipeline()

@app.route('/extract', methods=['POST'])
def extract():
    """API endpoint for extraction"""
    data = request.json
    text = data.get('text')
    
    entities, relations, _, _ = pipeline.run_extraction(text)
    
    return jsonify({
        'entities': entities,
        'relations': relations
    })
```

---

## 7. Advanced Configuration

### 7.1 Custom Confidence Scoring

Add confidence scores to extraction results:

```python
def extract_with_confidence(self, text: str) -> Dict:
    """Extract entities with confidence scores"""
    entities = self.extract_all(text)
    
    for entity_type, items in entities.items():
        for item in items:
            # Simple confidence based on completeness
            attrs_present = sum(1 for v in item.values() if v is not None)
            item['confidence'] = attrs_present / len(item)
    
    return entities
```

### 7.2 Cross-Validation

Setup k-fold cross-validation:

```python
from sklearn.model_selection import KFold

def cross_validate(documents: List[str], k: int = 5):
    """Perform k-fold cross-validation"""
    kf = KFold(n_splits=k)
    scores = []
    
    for train_idx, test_idx in kf.split(documents):
        train_docs = [documents[i] for i in train_idx]
        test_docs = [documents[i] for i in test_idx]
        
        # Train and evaluate
        score = evaluate_on_test_set(train_docs, test_docs)
        scores.append(score)
    
    return np.mean(scores), np.std(scores)
```

---

## 8. Troubleshooting

### Issue: Low Extraction Accuracy

**Solution 1**: Refine regex patterns
```python
# Before: Simple pattern
pattern = r'([A-Z][a-z]+)'

# After: More specific
pattern = r'(?:Mr|Ms|Dr)\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
```

**Solution 2**: Add preprocessing
```python
text = clean_text(text)
text = normalize_entities(text)
entities = self.extract_all(text)
```

### Issue: Memory Usage

**Solution**: Use generators for large datasets
```python
def extract_batch(self, documents: List[str], batch_size: int = 10):
    """Extract from documents in batches"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        yield self.extract_all('\n'.join(batch))
```

### Issue: Slow Extraction

**Solution**: Enable caching and parallel processing
```python
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor

@lru_cache(maxsize=1024)
def cached_extraction(text: str):
    return self.extract_all(text)

# Use ProcessPoolExecutor for parallel processing
```

---

## 9. Testing Custom Configurations

After making configuration changes, run tests:

```bash
# Run unit tests
python tests/test_kgeb.py

# Run specific test class
python -m unittest tests.test_kgeb.TestEntityExtraction

# Run with coverage
python -m coverage run -m unittest discover tests/
python -m coverage report
```

---

## 10. Best Practices

1. **Version Your Configurations**: Keep schema versions in `config/versions.json`
2. **Document Changes**: Maintain a `CHANGELOG.md` for configuration updates
3. **Test Incrementally**: Test each configuration change before deploying
4. **Monitor Performance**: Track extraction and evaluation metrics over time
5. **Backup Configurations**: Version control all configuration files
6. **Validate Input**: Always validate entity and relation schemas
7. **Handle Edge Cases**: Add tests for edge cases in your custom patterns
8. **Optimize Patterns**: Use `re.VERBOSE` for complex patterns

---

**Configuration Guide Version**: 1.0  
**Last Updated**: November 25, 2025
