"""
Comprehensive Test Suite for KGEB
Tests entity extraction, relation extraction, and evaluation framework
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entity_extractor import EntityExtractor
from relation_extractor import RelationExtractor
from evaluator import Evaluator, EvaluationMetrics


class TestEntityExtraction(unittest.TestCase):
    """Test entity extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.entities_schema = {
            "Person": ["name", "age", "position", "department"],
            "Company": ["name", "industry", "sector", "location"],
            "Project": ["name", "start_date", "end_date", "status", "budget"],
        }
        self.extractor = EntityExtractor(self.entities_schema)
        
        self.sample_text = """
        John Doe, age 32, works at OpenAI as a Researcher.
        Jane Smith, age 28, works at Google as an Engineer.
        Project Alpha started on 2023-01-15, ends on 2023-06-30.
        Project Beta began on 2023-02-01, concludes on 2023-08-15.
        """
    
    def test_person_extraction(self):
        """Test Person entity extraction"""
        persons = self.extractor.extract_persons(self.sample_text)
        self.assertGreater(len(persons), 0)
        self.assertEqual(persons[0]['name'], 'John Doe')
        self.assertEqual(persons[0]['age'], 32)
        self.assertEqual(persons[0]['position'], 'Researcher')
    
    def test_company_extraction(self):
        """Test Company entity extraction"""
        companies = self.extractor.extract_companies(self.sample_text)
        self.assertGreater(len(companies), 0)
        company_names = [c['name'] for c in companies]
        self.assertIn('OpenAI', company_names)
    
    def test_project_extraction(self):
        """Test Project entity extraction"""
        projects = self.extractor.extract_projects(self.sample_text)
        self.assertGreater(len(projects), 0)
        project_names = [p['name'] for p in projects]
        self.assertIn('Alpha', project_names)
        self.assertIn('Beta', project_names)
    
    def test_project_date_validation(self):
        """Test that invalid project dates are skipped"""
        text_with_invalid_date = """
        Project BadDate initiated on 2023-03-20, completes on 2023-07-40.
        """
        projects = self.extractor.extract_projects(text_with_invalid_date)
        # Should not extract invalid dates
        self.assertEqual(len(projects), 0)
    
    def test_extract_all(self):
        """Test extracting all entity types"""
        all_entities = self.extractor.extract_all(self.sample_text)
        self.assertIn('Person', all_entities)
        self.assertIn('Company', all_entities)
        self.assertIn('Project', all_entities)
    
    def test_json_serialization(self):
        """Test JSON serialization of entities"""
        self.extractor.extract_all(self.sample_text)
        json_str = self.extractor.to_json()
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, dict)


class TestRelationExtraction(unittest.TestCase):
    """Test relation extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.relations_schema = {
            "relation_types": [
                {
                    "id": 1,
                    "name": "BelongsTo",
                    "source_entity": "Person",
                    "target_entity": "Department"
                }
            ]
        }
        
        # Mock entities
        self.entities = {
            "Person": [
                {"name": "John Doe", "age": 32, "position": "Researcher", "department": "R&D"},
                {"name": "Jane Smith", "age": 28, "position": "Engineer", "department": "Engineering"}
            ],
            "Company": [
                {"name": "OpenAI", "industry": "Technology", "sector": "AI", "location": None},
                {"name": "Google", "industry": "Technology", "sector": "Internet", "location": None}
            ],
            "Project": [
                {"name": "Alpha", "start_date": "2023-01-15", "end_date": "2023-06-30", "status": "Completed", "budget": None}
            ]
        }
        
        self.extractor = RelationExtractor(self.relations_schema, self.entities)
    
    def test_works_at_extraction(self):
        """Test WorksAt relation extraction"""
        text = "John Doe, age 32, works at OpenAI as a Researcher."
        relations = self.extractor.extract_works_at(text)
        self.assertGreater(len(relations), 0)
        self.assertEqual(relations[0]['person'], 'John Doe')
        self.assertEqual(relations[0]['company'], 'OpenAI')
    
    def test_manages_project_extraction(self):
        """Test ManagesProject relation extraction"""
        text = "John Doe manages 3 projects: Alpha, Beta, Gamma."
        relations = self.extractor.extract_manages_project(text)
        self.assertGreater(len(relations), 0)
        self.assertEqual(relations[0]['person'], 'John Doe')
        self.assertIn(relations[0]['project'], ['Alpha', 'Beta', 'Gamma'])
    
    def test_owns_project_extraction(self):
        """Test OwnsProject relation extraction"""
        text = """
        John Doe, age 32, works at OpenAI as a Researcher.
        John Doe manages 1 project: Alpha.
        """
        relations = self.extractor.extract_owns_project(text)
        # This should infer that OpenAI owns Alpha
        self.assertGreater(len(relations), 0)


class TestEvaluationMetrics(unittest.TestCase):
    """Test evaluation metrics calculation"""
    
    def test_precision_recall_f1_perfect_match(self):
        """Test metrics with perfect match"""
        predicted = [{"name": "Alice"}, {"name": "Bob"}]
        truth = [{"name": "Alice"}, {"name": "Bob"}]
        
        precision, recall, f1 = EvaluationMetrics.calculate_precision_recall_f1(
            predicted, truth, match_keys=['name']
        )
        
        self.assertEqual(precision, 1.0)
        self.assertEqual(recall, 1.0)
        self.assertEqual(f1, 1.0)
    
    def test_precision_recall_f1_partial_match(self):
        """Test metrics with partial match"""
        predicted = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]
        truth = [{"name": "Alice"}, {"name": "Bob"}]
        
        precision, recall, f1 = EvaluationMetrics.calculate_precision_recall_f1(
            predicted, truth, match_keys=['name']
        )
        
        self.assertEqual(precision, 2/3)  # 2 correct, 1 false positive
        self.assertEqual(recall, 1.0)  # 2 correct, 0 false negative
        self.assertLess(f1, 1.0)
    
    def test_precision_recall_f1_no_match(self):
        """Test metrics with no match"""
        predicted = [{"name": "Charlie"}]
        truth = [{"name": "Alice"}, {"name": "Bob"}]
        
        precision, recall, f1 = EvaluationMetrics.calculate_precision_recall_f1(
            predicted, truth, match_keys=['name']
        )
        
        self.assertEqual(precision, 0.0)
        self.assertEqual(recall, 0.0)
        self.assertEqual(f1, 0.0)
    
    def test_schema_compliance(self):
        """Test schema compliance check"""
        entities = {
            "Person": [
                {"name": "Alice", "age": 30, "position": "Engineer", "department": "R&D"},
                {"name": "Bob", "age": 25, "position": "Designer"}  # Missing department
            ]
        }
        
        schema = {
            "Person": ["name", "age", "position", "department"]
        }
        
        compliance, details = EvaluationMetrics.check_schema_compliance(entities, schema)
        self.assertGreater(compliance, 0)
        self.assertLess(compliance, 100)  # Not 100% due to Bob
    
    def test_logical_consistency(self):
        """Test logical consistency check"""
        entities = {
            "Person": [{"name": "Alice"}],
            "Company": [{"name": "TechCorp"}],
            "Project": [{"name": "ProjectX"}]
        }
        
        relations = {
            "WorksAt": [{"person": "Alice", "company": "TechCorp"}],
            "ManagesProject": [{"person": "Alice", "project": "ProjectX"}]
        }
        
        score, issues = EvaluationMetrics.check_logical_consistency(entities, relations)
        self.assertEqual(len(issues), 0)
        self.assertEqual(score, 1.0)
    
    def test_logical_consistency_with_issues(self):
        """Test logical consistency with entity mismatches"""
        entities = {
            "Person": [{"name": "Alice"}],
            "Company": [{"name": "TechCorp"}],
            "Project": [{"name": "ProjectX"}]
        }
        
        relations = {
            "WorksAt": [{"person": "Bob", "company": "TechCorp"}],  # Bob not in Person
            "ManagesProject": [{"person": "Alice", "project": "ProjectY"}]  # ProjectY not in Project
        }
        
        score, issues = EvaluationMetrics.check_logical_consistency(entities, relations)
        self.assertGreater(len(issues), 0)
        self.assertLess(score, 1.0)


class TestEvaluator(unittest.TestCase):
    """Test evaluation framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.entities_schema = {
            "Person": ["name", "age", "position", "department"],
        }
        self.relations_schema = {"relation_types": []}
        self.evaluator = Evaluator(self.entities_schema, self.relations_schema)
    
    def test_evaluate_entities(self):
        """Test entity evaluation"""
        entities = {
            "Person": [
                {"name": "Alice", "age": 30, "position": "Engineer", "department": "R&D"}
            ]
        }
        
        results = self.evaluator.evaluate_entities(entities)
        self.assertIn('schema_compliance', results)
        self.assertGreater(results['schema_compliance']['percentage'], 0)
    
    def test_generate_report(self):
        """Test report generation"""
        entity_results = {
            "schema_compliance": {"percentage": 95.0, "details": {}},
            "entity_f1": 0.85
        }
        relation_results = {
            "logical_consistency": {"score": 0.92, "issues": []},
            "relation_f1": 0.78
        }
        
        report = self.evaluator.generate_report(entity_results, relation_results, "TestMethod")
        
        self.assertEqual(report['method'], 'TestMethod')
        self.assertIn('timestamp', report)
        self.assertEqual(report['overall_metrics']['entity_f1'], 0.85)
        self.assertEqual(report['overall_metrics']['relation_f1'], 0.78)


class TestPersistence(unittest.TestCase):
    """Test data persistence and file handling"""
    
    def test_save_entities_to_file(self):
        """Test saving entities to JSON file"""
        entities_schema = {"Person": ["name", "age"]}
        extractor = EntityExtractor(entities_schema)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            text = "John Doe, age 32, works at OpenAI as a Researcher."
            extractor.extract_all(text)
            extractor.save_to_file(temp_file)
            
            # Verify file was created and contains valid JSON
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, dict)
            self.assertIn('Person', data)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_save_report_to_file(self):
        """Test saving evaluation report to file"""
        evaluator = Evaluator({"Person": ["name"]}, {})
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            report = {
                "method": "Test",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "entity_f1": 0.85,
                "relation_f1": 0.78
            }
            evaluator.save_report(report, temp_file)
            
            # Verify file was created
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['method'], 'Test')
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def test_multi_document_behavior(self):
        """Test extraction from multiple documents"""
        doc1 = "John Doe, age 32, works at OpenAI as a Researcher."
        doc2 = "Jane Smith, age 28, works at Google as an Engineer."
        
        schema = {"Person": ["name", "age", "position", "department"]}
        extractor = EntityExtractor(schema)
        
        # Extract from document 1
        entities1 = extractor.extract_all(doc1)
        
        # Extract from document 2
        entities2 = extractor.extract_all(doc2)
        
        self.assertEqual(len(entities2['Person']), 1)
        self.assertEqual(entities2['Person'][0]['name'], 'Jane Smith')
    
    def test_conflict_handling(self):
        """Test handling of conflicting information"""
        text = """
        John Doe, age 32, works at OpenAI as a Researcher.
        John Doe, age 35, works at Google as a Senior Researcher.
        """
        
        schema = {"Person": ["name", "age", "position", "department"]}
        extractor = EntityExtractor(schema)
        persons = extractor.extract_persons(text)
        
        # Should extract both mentions (may have duplicates/conflicts)
        self.assertGreater(len(persons), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline"""
    
    def test_end_to_end_pipeline(self):
        """Test complete extraction and evaluation pipeline"""
        text = """
        John Doe, age 32, works at OpenAI as a Researcher.
        Jane Smith, age 28, works at Google as an Engineer.
        Michael Brown, age 45, works at Microsoft as a Senior Developer.
        
        Project Alpha started on 2023-01-15, ends on 2023-06-30.
        Project Beta began on 2023-02-01, concludes on 2023-08-15.
        
        John Doe manages 1 project: Alpha.
        Jane Smith leads 1 project: Beta.
        
        OpenAI operates in the Technology industry.
        Google specializes in Technology and Internet Services.
        Microsoft focuses on Technology and Software industry.
        """
        
        # Extract entities
        entities_schema = {
            "Person": ["name", "age", "position", "department"],
            "Company": ["name", "industry", "sector", "location"],
            "Project": ["name", "start_date", "end_date", "status", "budget"],
        }
        
        entity_extractor = EntityExtractor(entities_schema)
        entities = entity_extractor.extract_all(text)
        
        # Extract relations
        relations_schema = {"relation_types": []}
        relation_extractor = RelationExtractor(relations_schema, entities)
        relations = relation_extractor.extract_all(text)
        
        # Evaluate
        evaluator = Evaluator(entities_schema, relations_schema)
        entity_results = evaluator.evaluate_entities(entities)
        relation_results = evaluator.evaluate_relations(relations, entities)
        
        report = evaluator.generate_report(entity_results, relation_results)
        
        # Verify results
        self.assertGreater(len(entities['Person']), 0)
        self.assertGreater(len(entities['Company']), 0)
        self.assertGreater(len(entities['Project']), 0)
        self.assertIn('schema_compliance', report['entity_evaluation'])


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEntityExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestRelationExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluationMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
