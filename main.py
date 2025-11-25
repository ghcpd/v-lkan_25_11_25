"""
Enterprise Knowledge Graph Extraction Benchmark (KGEB)
Main Pipeline and CLI

This module provides the main entry point and command-line interface for KGEB
"""

import click
import json
import os
from pathlib import Path
from datetime import datetime
import colorlog
import logging

from entity_extractor import EntityExtractor
from relation_extractor import RelationExtractor
from evaluator import KGEBEvaluator


# Configure colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger('KGEB')
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class KGEBPipeline:
    """Main pipeline for KGEB operations"""
    
    def __init__(self, 
                 documents_path: str = "documents.txt",
                 entities_schema_path: str = "entities.json",
                 relations_schema_path: str = "relations.json",
                 output_dir: str = "output"):
        """
        Initialize KGEB pipeline
        
        Args:
            documents_path: Path to input documents
            entities_schema_path: Path to entities schema
            relations_schema_path: Path to relations schema
            output_dir: Directory for output files
        """
        self.documents_path = documents_path
        self.entities_schema_path = entities_schema_path
        self.relations_schema_path = relations_schema_path
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.entity_extractor = None
        self.relation_extractor = None
        self.evaluator = None
    
    def extract_entities(self) -> str:
        """
        Extract entities from documents
        
        Returns:
            Path to entities output file
        """
        logger.info("🔍 Starting entity extraction...")
        
        self.entity_extractor = EntityExtractor(self.entities_schema_path)
        entities = self.entity_extractor.extract_from_file(self.documents_path)
        
        output_path = os.path.join(self.output_dir, "entities_output.json")
        self.entity_extractor.save_to_json(output_path)
        
        stats = self.entity_extractor.get_statistics()
        logger.info(f"✅ Entity extraction complete: {sum(stats.values())} total entities")
        
        for entity_type, count in stats.items():
            logger.info(f"   • {entity_type}: {count}")
        
        return output_path
    
    def extract_relations(self, entities_path: str = None) -> str:
        """
        Extract relations from documents
        
        Args:
            entities_path: Path to entities file (optional)
            
        Returns:
            Path to relations output file
        """
        logger.info("🔗 Starting relation extraction...")
        
        if entities_path is None:
            entities_path = os.path.join(self.output_dir, "entities_output.json")
        
        self.relation_extractor = RelationExtractor(self.relations_schema_path)
        
        try:
            self.relation_extractor.load_entities(entities_path)
        except FileNotFoundError:
            logger.warning("⚠️  Entities file not found. Relations may be incomplete.")
        
        relations = self.relation_extractor.extract_from_file(self.documents_path)
        
        output_path = os.path.join(self.output_dir, "relations_output.json")
        self.relation_extractor.save_to_json(output_path)
        
        stats = self.relation_extractor.get_statistics()
        logger.info(f"✅ Relation extraction complete: {sum(stats.values())} total relations")
        
        for relation_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"   • {relation_type}: {count}")
        
        if len(stats) > 10:
            logger.info(f"   ... and {len(stats) - 10} more relation types")
        
        return output_path
    
    def evaluate(self, 
                method_name: str = "KGEB Baseline",
                entities_predicted: str = None,
                relations_predicted: str = None,
                entities_ground_truth: str = None,
                relations_ground_truth: str = None) -> str:
        """
        Evaluate extraction results
        
        Args:
            method_name: Name of the extraction method
            entities_predicted: Path to predicted entities (optional)
            relations_predicted: Path to predicted relations (optional)
            entities_ground_truth: Path to ground truth entities (optional)
            relations_ground_truth: Path to ground truth relations (optional)
            
        Returns:
            Path to evaluation report
        """
        logger.info("📊 Starting evaluation...")
        
        if entities_predicted is None:
            entities_predicted = os.path.join(self.output_dir, "entities_output.json")
        
        if relations_predicted is None:
            relations_predicted = os.path.join(self.output_dir, "relations_output.json")
        
        self.evaluator = KGEBEvaluator(self.entities_schema_path, self.relations_schema_path)
        
        output_path = os.path.join(self.output_dir, "evaluation_report.json")
        
        report = self.evaluator.generate_report(
            method_name=method_name,
            entities_predicted=entities_predicted,
            relations_predicted=relations_predicted,
            entities_ground_truth=entities_ground_truth,
            relations_ground_truth=relations_ground_truth,
            output_path=output_path
        )
        
        logger.info("✅ Evaluation complete")
        self.evaluator.print_summary(report)
        
        return output_path
    
    def run_full_pipeline(self, method_name: str = "KGEB Baseline"):
        """
        Run the complete extraction and evaluation pipeline
        
        Args:
            method_name: Name of the extraction method
        """
        logger.info("🚀 Starting KGEB full pipeline...")
        logger.info(f"   Documents: {self.documents_path}")
        logger.info(f"   Output directory: {self.output_dir}")
        
        # Extract entities
        entities_path = self.extract_entities()
        
        # Extract relations
        relations_path = self.extract_relations(entities_path)
        
        # Evaluate
        report_path = self.evaluate(method_name=method_name)
        
        logger.info(f"\n🎉 Pipeline complete! Results saved to {self.output_dir}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Enterprise Knowledge Graph Extraction Benchmark (KGEB)
    
    A framework for evaluating AI methods on entity recognition 
    and relation extraction from enterprise text.
    """
    pass


@cli.command()
@click.option('--documents', '-d', default="documents.txt", 
              help='Path to documents file')
@click.option('--entities-schema', '-e', default="entities.json",
              help='Path to entities schema file')
@click.option('--output', '-o', default="output/entities_output.json",
              help='Path to output file')
def extract_entities(documents, entities_schema, output):
    """Extract entities from documents"""
    logger.info(f"Extracting entities from {documents}...")
    
    extractor = EntityExtractor(entities_schema)
    entities = extractor.extract_from_file(documents)
    extractor.save_to_json(output)
    
    stats = extractor.get_statistics()
    logger.info(f"✅ Extracted {sum(stats.values())} entities")
    
    for entity_type, count in stats.items():
        logger.info(f"   • {entity_type}: {count}")


@cli.command()
@click.option('--documents', '-d', default="documents.txt",
              help='Path to documents file')
@click.option('--entities', '-e', default="output/entities_output.json",
              help='Path to entities file')
@click.option('--relations-schema', '-r', default="relations.json",
              help='Path to relations schema file')
@click.option('--output', '-o', default="output/relations_output.json",
              help='Path to output file')
def extract_relations(documents, entities, relations_schema, output):
    """Extract relations from documents"""
    logger.info(f"Extracting relations from {documents}...")
    
    extractor = RelationExtractor(relations_schema)
    
    try:
        extractor.load_entities(entities)
    except FileNotFoundError:
        logger.warning("⚠️  Entities file not found. Run entity extraction first.")
    
    relations = extractor.extract_from_file(documents)
    extractor.save_to_json(output)
    
    stats = extractor.get_statistics()
    logger.info(f"✅ Extracted {sum(stats.values())} relations")
    
    for relation_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"   • {relation_type}: {count}")


@cli.command()
@click.option('--method', '-m', default="KGEB Baseline",
              help='Name of the extraction method')
@click.option('--entities-predicted', '-e', default="output/entities_output.json",
              help='Path to predicted entities')
@click.option('--relations-predicted', '-r', default="output/relations_output.json",
              help='Path to predicted relations')
@click.option('--entities-gt', default=None,
              help='Path to ground truth entities (optional)')
@click.option('--relations-gt', default=None,
              help='Path to ground truth relations (optional)')
@click.option('--output', '-o', default="output/evaluation_report.json",
              help='Path to output report')
def evaluate(method, entities_predicted, relations_predicted, entities_gt, relations_gt, output):
    """Evaluate extraction results"""
    logger.info(f"Evaluating method: {method}...")
    
    evaluator = KGEBEvaluator()
    
    report = evaluator.generate_report(
        method_name=method,
        entities_predicted=entities_predicted,
        relations_predicted=relations_predicted,
        entities_ground_truth=entities_gt,
        relations_ground_truth=relations_gt,
        output_path=output
    )
    
    evaluator.print_summary(report)


@cli.command()
@click.option('--documents', '-d', default="documents.txt",
              help='Path to documents file')
@click.option('--method', '-m', default="KGEB Baseline",
              help='Name of the extraction method')
@click.option('--output-dir', '-o', default="output",
              help='Output directory')
def run(documents, method, output_dir):
    """Run the complete KGEB pipeline"""
    pipeline = KGEBPipeline(
        documents_path=documents,
        output_dir=output_dir
    )
    
    pipeline.run_full_pipeline(method_name=method)


@cli.command()
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def test(verbose):
    """Run KGEB test suite"""
    import pytest
    
    args = ["test_kgeb.py", "-v"]
    if verbose:
        args.append("--tb=long")
    else:
        args.append("--tb=short")
    
    logger.info("🧪 Running KGEB test suite...")
    pytest.main(args)


@cli.command()
def info():
    """Display KGEB information"""
    info_text = """
╔════════════════════════════════════════════════════════════════════╗
║  Enterprise Knowledge Graph Extraction Benchmark (KGEB) v1.0.0    ║
╚════════════════════════════════════════════════════════════════════╝

📋 Project Structure:
   • documents.txt          - Input documents
   • entities.json          - Entity schema (10 types)
   • relations.json         - Relation schema (30 types)
   • entity_extractor.py    - Entity extraction module
   • relation_extractor.py  - Relation extraction module
   • evaluator.py           - Evaluation framework
   • test_kgeb.py           - Test suite
   • main.py                - CLI and pipeline

📊 Capabilities:
   • Extract 10 entity types with attributes
   • Extract 30 relation types between entities
   • Evaluate with precision, recall, F1 metrics
   • Check schema compliance
   • Validate logical consistency
   • Generate comprehensive reports

🔧 Usage:
   kgeb run                 - Run full pipeline
   kgeb extract-entities    - Extract entities only
   kgeb extract-relations   - Extract relations only
   kgeb evaluate            - Evaluate results
   kgeb test                - Run tests
   kgeb --help              - Show help

📚 Documentation: See README.md for details
"""
    print(info_text)


@cli.command()
@click.option('--entities', '-e', default="output/entities_output.json",
              help='Path to entities file')
@click.option('--relations', '-r', default="output/relations_output.json",
              help='Path to relations file')
def stats(entities, relations):
    """Display statistics about extracted data"""
    logger.info("📈 KGEB Statistics")
    
    if os.path.exists(entities):
        with open(entities, 'r') as f:
            entities_data = json.load(f)
        
        logger.info("\n📊 Entity Statistics:")
        total = 0
        for entity_type, entity_list in sorted(entities_data.items()):
            count = len(entity_list)
            total += count
            logger.info(f"   • {entity_type:20s}: {count:4d}")
        logger.info(f"   {'Total':20s}: {total:4d}")
    else:
        logger.warning(f"⚠️  Entities file not found: {entities}")
    
    if os.path.exists(relations):
        with open(relations, 'r') as f:
            relations_data = json.load(f)
        
        logger.info("\n🔗 Relation Statistics:")
        total = 0
        sorted_relations = sorted(relations_data.items(), key=lambda x: len(x[1]), reverse=True)
        
        for relation_type, relation_list in sorted_relations[:15]:
            count = len(relation_list)
            total += count
            logger.info(f"   • {relation_type:30s}: {count:4d}")
        
        if len(sorted_relations) > 15:
            remaining = sum(len(r[1]) for r in sorted_relations[15:])
            total += remaining
            logger.info(f"   • ... and {len(sorted_relations) - 15} more types: {remaining:4d}")
        
        logger.info(f"   {'Total':30s}: {total:4d}")
    else:
        logger.warning(f"⚠️  Relations file not found: {relations}")


if __name__ == "__main__":
    cli()
