"""
KGEB Pipeline Runner
Main entry point for running the complete KGEB pipeline
"""

import os
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from entity_extractor import EntityExtractor
from relation_extractor import RelationExtractor
from evaluator import Evaluator


class KGEBPipeline:
    """Main pipeline for KGEB"""
    
    def __init__(self, data_dir='data', config_dir='config', output_dir='output'):
        """Initialize KGEB pipeline"""
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Load schemas
        self.load_schemas()
    
    def load_schemas(self):
        """Load entity and relation schemas"""
        with open(self.config_dir / 'entities.json', 'r', encoding='utf-8') as f:
            self.entities_schema = json.load(f)
        
        with open(self.config_dir / 'relations.json', 'r', encoding='utf-8') as f:
            self.relations_schema = json.load(f)
        
        print("Schemas loaded successfully")
    
    def run_extraction(self, input_file):
        """Run entity and relation extraction"""
        print(f"\n{'='*60}")
        print("ENTITY AND RELATION EXTRACTION")
        print(f"{'='*60}")
        
        # Read input document
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Processing document: {input_file}")
        print(f"Document size: {len(text)} characters")
        
        # Extract entities
        print("\n[1/3] Extracting entities...")
        entity_extractor = EntityExtractor(self.entities_schema)
        entities = entity_extractor.extract_all(text)
        
        # Save entities
        entities_output_file = self.output_dir / 'entities_output.json'
        entity_extractor.save_to_file(str(entities_output_file))
        
        # Print entity summary
        print("\nEntity Extraction Results:")
        for entity_type, items in entities.items():
            print(f"  {entity_type}: {len(items)} entities")
        
        # Extract relations
        print("\n[2/3] Extracting relations...")
        relation_extractor = RelationExtractor(self.relations_schema, entities)
        relations = relation_extractor.extract_all(text)
        
        # Save relations
        relations_output_file = self.output_dir / 'relations_output.json'
        relation_extractor.save_to_file(str(relations_output_file))
        
        # Print relation summary
        print("\nRelation Extraction Results:")
        for relation_type, items in relations.items():
            if items:
                print(f"  {relation_type}: {len(items)} relations")
        
        return entities, relations, entities_output_file, relations_output_file
    
    def run_evaluation(self, entities_file, relations_file, method_name="KGEB Pipeline"):
        """Run evaluation"""
        print(f"\n{'='*60}")
        print("EVALUATION")
        print(f"{'='*60}")
        
        # Load extraction results
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        with open(relations_file, 'r', encoding='utf-8') as f:
            relations = json.load(f)
        
        # Evaluate
        print("\n[3/3] Evaluating extraction results...")
        evaluator = Evaluator(self.entities_schema, self.relations_schema)
        
        entity_results = evaluator.evaluate_entities(entities)
        relation_results = evaluator.evaluate_relations(relations, entities)
        
        report = evaluator.generate_report(entity_results, relation_results, method_name)
        
        # Save report
        report_file = self.output_dir / 'evaluation_report.json'
        evaluator.save_report(report, str(report_file))
        
        # Print evaluation summary
        print("\nEvaluation Results:")
        print(f"  Entity F1: {report['overall_metrics']['entity_f1']:.2%}")
        print(f"  Relation F1: {report['overall_metrics']['relation_f1']:.2%}")
        print(f"  Schema Compliance: {report['overall_metrics']['schema_compliance']:.2%}")
        print(f"  Logical Consistency: {report['overall_metrics']['logical_consistency']:.2%}")
        
        return report, report_file
    
    def run_full_pipeline(self, input_file, method_name="KGEB Pipeline"):
        """Run complete KGEB pipeline"""
        print(f"\n{'#'*60}")
        print("# KGEB - Enterprise Knowledge Graph Extraction Benchmark")
        print(f"{'#'*60}")
        
        # Extraction phase
        entities, relations, entities_file, relations_file = self.run_extraction(input_file)
        
        # Evaluation phase
        report, report_file = self.run_evaluation(entities_file, relations_file, method_name)
        
        print(f"\n{'='*60}")
        print("RESULTS SAVED")
        print(f"{'='*60}")
        print(f"Entities: {entities_file}")
        print(f"Relations: {relations_file}")
        print(f"Report: {report_file}")
        
        return report


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <input_document> [method_name]")
        print("\nExample: python pipeline.py ../documents.txt 'My Extraction Method'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    method_name = sys.argv[2] if len(sys.argv) > 2 else "KGEB Pipeline"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Run pipeline
    pipeline = KGEBPipeline()
    report = pipeline.run_full_pipeline(input_file, method_name)
    
    print(f"\n{'#'*60}")
    print("# PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
