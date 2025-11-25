"""
Enterprise Knowledge Graph Extraction Benchmark (KGEB)
Comprehensive Test Suite

This module provides automated tests for all KGEB components
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from entity_extractor import EntityExtractor
from relation_extractor import RelationExtractor
from evaluator import KGEBEvaluator


class TestEntityExtractor:
    """Test suite for EntityExtractor"""
    
    @pytest.fixture
    def sample_document(self):
        """Create a sample document for testing"""
        return """John Doe, age 32, works at OpenAI as a Researcher.
Jane Smith, age 28, works at Google as an Engineer.

OpenAI operates in the Technology industry.
Google specializes in Technology and Internet Services.

Project Alpha started on 2023-01-15, ends on 2023-06-30.
Project Beta began on 2023-02-01, concludes on 2023-08-15.
"""
    
    @pytest.fixture
    def entities_schema(self):
        """Sample entities schema"""
        return {
            "Person": ["name", "age", "position", "department"],
            "Company": ["name", "industry", "sector", "location"],
            "Project": ["name", "start_date", "end_date", "status", "budget"]
        }
    
    @pytest.fixture
    def extractor(self, tmp_path, entities_schema):
        """Create EntityExtractor with temp schema file"""
        schema_file = tmp_path / "entities.json"
        with open(schema_file, 'w') as f:
            json.dump(entities_schema, f)
        
        return EntityExtractor(str(schema_file))
    
    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes correctly"""
        assert extractor.schema is not None
        assert "Person" in extractor.schema
        assert "Company" in extractor.schema
        assert "Project" in extractor.schema
    
    def test_extract_person(self, extractor, tmp_path, sample_document):
        """Test person entity extraction"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        entities = extractor.extract_from_file(str(doc_file))
        
        assert "Person" in entities
        assert len(entities["Person"]) >= 2
        
        # Check if John Doe is extracted
        john = next((p for p in entities["Person"] if p["name"] == "John Doe"), None)
        assert john is not None
        assert john["age"] == 32
        assert john["position"] == "Researcher"
    
    def test_extract_company(self, extractor, tmp_path, sample_document):
        """Test company entity extraction"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        entities = extractor.extract_from_file(str(doc_file))
        
        assert "Company" in entities
        assert len(entities["Company"]) >= 2
        
        # Check if OpenAI is extracted
        openai = next((c for c in entities["Company"] if c["name"] == "OpenAI"), None)
        assert openai is not None
        assert "Technology" in openai["industry"]
    
    def test_extract_project(self, extractor, tmp_path, sample_document):
        """Test project entity extraction"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        entities = extractor.extract_from_file(str(doc_file))
        
        assert "Project" in entities
        assert len(entities["Project"]) >= 2
        
        # Check if Project Alpha is extracted
        alpha = next((p for p in entities["Project"] if p["name"] == "Alpha"), None)
        assert alpha is not None
        assert alpha["start_date"] == "2023-01-15"
        assert alpha["end_date"] == "2023-06-30"
    
    def test_save_entities(self, extractor, tmp_path, sample_document):
        """Test saving entities to JSON"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        output_file = tmp_path / "entities_output.json"
        extractor.extract_from_file(str(doc_file))
        extractor.save_to_json(str(output_file))
        
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            saved_entities = json.load(f)
        
        assert "Person" in saved_entities
        assert isinstance(saved_entities["Person"], list)
    
    def test_deduplication(self, extractor, tmp_path):
        """Test that duplicate entities are removed"""
        doc_file = tmp_path / "test_doc.txt"
        duplicate_doc = """John Doe, age 32, works at OpenAI as a Researcher.
John Doe, age 32, works at OpenAI as a Researcher.
"""
        with open(doc_file, 'w') as f:
            f.write(duplicate_doc)
        
        entities = extractor.extract_from_file(str(doc_file))
        
        # Should have only one John Doe
        john_count = len([p for p in entities["Person"] if p["name"] == "John Doe"])
        assert john_count == 1


class TestRelationExtractor:
    """Test suite for RelationExtractor"""
    
    @pytest.fixture
    def sample_document(self):
        """Create a sample document for testing"""
        return """John Doe, age 32, works at OpenAI as a Researcher.
Jane Smith, age 28, works at Google as an Engineer.

John Doe manages 3 projects: Alpha, Beta, Gamma.
Jane Smith leads 2 projects: Delta, Epsilon.

OpenAI operates in the Technology industry.
Google specializes in Technology and Internet Services.
"""
    
    @pytest.fixture
    def sample_entities(self, tmp_path):
        """Create sample entities file"""
        entities = {
            "Person": [
                {"name": "John Doe", "age": 32, "position": "Researcher", "department": "R&D"},
                {"name": "Jane Smith", "age": 28, "position": "Engineer", "department": "Engineering"}
            ],
            "Company": [
                {"name": "OpenAI", "industry": "Technology", "sector": "AI", "location": "San Francisco"},
                {"name": "Google", "industry": "Technology", "sector": "Internet Services", "location": "Mountain View"}
            ],
            "Project": [
                {"name": "Alpha", "start_date": "2023-01-15", "end_date": "2023-06-30", "status": "Ongoing", "budget": 500000}
            ]
        }
        
        entities_file = tmp_path / "entities.json"
        with open(entities_file, 'w') as f:
            json.dump(entities, f)
        
        return str(entities_file)
    
    @pytest.fixture
    def relations_schema(self, tmp_path):
        """Create sample relations schema"""
        schema = {
            "relations": [
                {"name": "WorksAt", "source_entity": "Person", "target_entity": "Company", "attributes": ["position"]},
                {"name": "ManagesProject", "source_entity": "Person", "target_entity": "Project", "attributes": ["responsibility_level"]}
            ]
        }
        
        schema_file = tmp_path / "relations.json"
        with open(schema_file, 'w') as f:
            json.dump(schema, f)
        
        return str(schema_file)
    
    @pytest.fixture
    def extractor(self, relations_schema):
        """Create RelationExtractor"""
        return RelationExtractor(relations_schema)
    
    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes correctly"""
        assert extractor.schema is not None
        assert len(extractor.schema) >= 2
    
    def test_extract_works_at(self, extractor, tmp_path, sample_document, sample_entities):
        """Test WorksAt relation extraction"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        extractor.load_entities(sample_entities)
        relations = extractor.extract_from_file(str(doc_file))
        
        assert "WorksAt" in relations
        assert len(relations["WorksAt"]) >= 2
        
        # Check if John Doe works at OpenAI
        john_openai = next((r for r in relations["WorksAt"] 
                           if r["person"] == "John Doe" and r["company"] == "OpenAI"), None)
        assert john_openai is not None
        assert john_openai["position"] == "Researcher"
    
    def test_extract_manages_project(self, extractor, tmp_path, sample_document, sample_entities):
        """Test ManagesProject relation extraction"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        extractor.load_entities(sample_entities)
        relations = extractor.extract_from_file(str(doc_file))
        
        assert "ManagesProject" in relations
        assert len(relations["ManagesProject"]) >= 3
        
        # Check if John Doe manages Alpha
        john_alpha = next((r for r in relations["ManagesProject"] 
                          if r["person"] == "John Doe" and r["project"] == "Alpha"), None)
        assert john_alpha is not None
    
    def test_save_relations(self, extractor, tmp_path, sample_document, sample_entities):
        """Test saving relations to JSON"""
        doc_file = tmp_path / "test_doc.txt"
        with open(doc_file, 'w') as f:
            f.write(sample_document)
        
        output_file = tmp_path / "relations_output.json"
        extractor.load_entities(sample_entities)
        extractor.extract_from_file(str(doc_file))
        extractor.save_to_json(str(output_file))
        
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            saved_relations = json.load(f)
        
        assert isinstance(saved_relations, dict)


class TestKGEBEvaluator:
    """Test suite for KGEBEvaluator"""
    
    @pytest.fixture
    def sample_entities_predicted(self, tmp_path):
        """Create sample predicted entities"""
        entities = {
            "Person": [
                {"name": "John Doe", "age": 32, "position": "Researcher", "department": "R&D"},
                {"name": "Jane Smith", "age": 28, "position": "Engineer", "department": "Engineering"}
            ],
            "Company": [
                {"name": "OpenAI", "industry": "Technology", "sector": "AI", "location": "San Francisco"}
            ]
        }
        
        file_path = tmp_path / "entities_predicted.json"
        with open(file_path, 'w') as f:
            json.dump(entities, f)
        
        return str(file_path)
    
    @pytest.fixture
    def sample_entities_ground_truth(self, tmp_path):
        """Create sample ground truth entities"""
        entities = {
            "Person": [
                {"name": "John Doe", "age": 32, "position": "Researcher", "department": "R&D"},
                {"name": "Jane Smith", "age": 28, "position": "Engineer", "department": "Engineering"},
                {"name": "Bob Johnson", "age": 45, "position": "Manager", "department": "Management"}
            ],
            "Company": [
                {"name": "OpenAI", "industry": "Technology", "sector": "AI", "location": "San Francisco"}
            ]
        }
        
        file_path = tmp_path / "entities_ground_truth.json"
        with open(file_path, 'w') as f:
            json.dump(entities, f)
        
        return str(file_path)
    
    @pytest.fixture
    def sample_relations_predicted(self, tmp_path):
        """Create sample predicted relations"""
        relations = {
            "WorksAt": [
                {"person": "John Doe", "company": "OpenAI", "position": "Researcher", "start_date": "2020-01-01"}
            ]
        }
        
        file_path = tmp_path / "relations_predicted.json"
        with open(file_path, 'w') as f:
            json.dump(relations, f)
        
        return str(file_path)
    
    @pytest.fixture
    def entities_schema(self, tmp_path):
        """Create entities schema"""
        schema = {
            "Person": ["name", "age", "position", "department"],
            "Company": ["name", "industry", "sector", "location"]
        }
        
        file_path = tmp_path / "entities_schema.json"
        with open(file_path, 'w') as f:
            json.dump(schema, f)
        
        return str(file_path)
    
    @pytest.fixture
    def relations_schema(self, tmp_path):
        """Create relations schema"""
        schema = {
            "relations": [
                {"name": "WorksAt", "source_entity": "Person", "target_entity": "Company", "attributes": ["position"]}
            ]
        }
        
        file_path = tmp_path / "relations_schema.json"
        with open(file_path, 'w') as f:
            json.dump(schema, f)
        
        return str(file_path)
    
    @pytest.fixture
    def evaluator(self, entities_schema, relations_schema):
        """Create KGEBEvaluator"""
        return KGEBEvaluator(entities_schema, relations_schema)
    
    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly"""
        assert evaluator.entities_schema is not None
        assert evaluator.relations_schema is not None
    
    def test_evaluate_entities_without_ground_truth(self, evaluator, sample_entities_predicted):
        """Test entity evaluation without ground truth"""
        result = evaluator.evaluate_entities(sample_entities_predicted)
        
        assert "schema_compliance" in result
        assert "statistics" in result
        assert "performance" in result
        assert result["performance"]["f1_score"] is None
    
    def test_evaluate_entities_with_ground_truth(self, evaluator, sample_entities_predicted, sample_entities_ground_truth):
        """Test entity evaluation with ground truth"""
        result = evaluator.evaluate_entities(sample_entities_predicted, sample_entities_ground_truth)
        
        assert "schema_compliance" in result
        assert "statistics" in result
        assert "performance" in result
        assert result["performance"]["f1_score"] is not None
        assert 0 <= result["performance"]["precision"] <= 1
        assert 0 <= result["performance"]["recall"] <= 1
    
    def test_evaluate_relations(self, evaluator, sample_relations_predicted, sample_entities_predicted):
        """Test relation evaluation"""
        result = evaluator.evaluate_relations(sample_relations_predicted, sample_entities_predicted)
        
        assert "schema_compliance" in result
        assert "logical_consistency" in result
        assert "statistics" in result
        assert "performance" in result
    
    def test_generate_report(self, evaluator, tmp_path, sample_entities_predicted, sample_relations_predicted):
        """Test report generation"""
        output_path = tmp_path / "test_report.json"
        
        report = evaluator.generate_report(
            method_name="Test Method",
            entities_predicted=sample_entities_predicted,
            relations_predicted=sample_relations_predicted,
            output_path=str(output_path)
        )
        
        assert output_path.exists()
        assert "method" in report
        assert report["method"] == "Test Method"
        assert "timestamp" in report
        assert "entity_evaluation" in report
        assert "relation_evaluation" in report


class TestIntegration:
    """Integration tests for the entire pipeline"""
    
    def test_full_pipeline(self, tmp_path):
        """Test the complete extraction and evaluation pipeline"""
        # Create test document
        doc_content = """John Doe, age 32, works at OpenAI as a Researcher.
Jane Smith, age 28, works at Google as an Engineer.

John Doe manages 3 projects: Alpha, Beta, Gamma.

OpenAI operates in the Technology industry.
Google specializes in Technology and Internet Services.

Project Alpha started on 2023-01-15, ends on 2023-06-30.
"""
        
        doc_file = tmp_path / "test_documents.txt"
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        # Create schemas
        entities_schema = {
            "Person": ["name", "age", "position", "department"],
            "Company": ["name", "industry", "sector", "location"],
            "Project": ["name", "start_date", "end_date", "status", "budget"]
        }
        
        entities_schema_file = tmp_path / "entities.json"
        with open(entities_schema_file, 'w') as f:
            json.dump(entities_schema, f)
        
        relations_schema = {
            "relations": [
                {"name": "WorksAt", "source_entity": "Person", "target_entity": "Company", "attributes": ["position"]},
                {"name": "ManagesProject", "source_entity": "Person", "target_entity": "Project", "attributes": []}
            ]
        }
        
        relations_schema_file = tmp_path / "relations.json"
        with open(relations_schema_file, 'w') as f:
            json.dump(relations_schema, f)
        
        # Extract entities
        entity_extractor = EntityExtractor(str(entities_schema_file))
        entities = entity_extractor.extract_from_file(str(doc_file))
        
        entities_output = tmp_path / "entities_output.json"
        entity_extractor.save_to_json(str(entities_output))
        
        # Extract relations
        relation_extractor = RelationExtractor(str(relations_schema_file))
        relation_extractor.load_entities(str(entities_output))
        relations = relation_extractor.extract_from_file(str(doc_file))
        
        relations_output = tmp_path / "relations_output.json"
        relation_extractor.save_to_json(str(relations_output))
        
        # Evaluate
        evaluator = KGEBEvaluator(str(entities_schema_file), str(relations_schema_file))
        report = evaluator.generate_report(
            method_name="Integration Test Method",
            entities_predicted=str(entities_output),
            relations_predicted=str(relations_output),
            output_path=str(tmp_path / "evaluation_report.json")
        )
        
        # Assertions
        assert entities_output.exists()
        assert relations_output.exists()
        assert (tmp_path / "evaluation_report.json").exists()
        assert report["method"] == "Integration Test Method"
        assert report["entity_evaluation"]["total_entities"] > 0
        assert report["relation_evaluation"]["total_relations"] > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
