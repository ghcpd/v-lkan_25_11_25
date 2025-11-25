"""
Enterprise Knowledge Graph Extraction Benchmark (KGEB)
Evaluation Framework

This module provides comprehensive evaluation metrics for entity and relation extraction
"""

import json
from typing import Dict, List, Any, Tuple, Set
from datetime import datetime
from collections import defaultdict
import jsonschema


class KGEBEvaluator:
    """Evaluate knowledge graph extraction methods"""
    
    def __init__(self, 
                 entities_schema_path: str = "entities.json",
                 relations_schema_path: str = "relations.json"):
        """
        Initialize the evaluator
        
        Args:
            entities_schema_path: Path to entities schema
            relations_schema_path: Path to relations schema
        """
        self.entities_schema = self._load_json(entities_schema_path)
        self.relations_schema = self._load_json(relations_schema_path)
        
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_entities(self, 
                         predicted_path: str,
                         ground_truth_path: str = None) -> Dict[str, Any]:
        """
        Evaluate entity extraction
        
        Args:
            predicted_path: Path to predicted entities JSON
            ground_truth_path: Path to ground truth entities (optional)
            
        Returns:
            Evaluation metrics dictionary
        """
        predicted = self._load_json(predicted_path)
        
        # Schema compliance check
        schema_compliance = self._check_entity_schema_compliance(predicted)
        
        # Statistics
        statistics = self._compute_entity_statistics(predicted)
        
        # If ground truth is provided, compute precision/recall/F1
        if ground_truth_path:
            ground_truth = self._load_json(ground_truth_path)
            performance = self._compute_entity_performance(predicted, ground_truth)
        else:
            performance = {
                "precision": None,
                "recall": None,
                "f1_score": None,
                "note": "Ground truth not provided"
            }
        
        return {
            "schema_compliance": schema_compliance,
            "statistics": statistics,
            "performance": performance
        }
    
    def evaluate_relations(self,
                          predicted_path: str,
                          entities_path: str,
                          ground_truth_path: str = None) -> Dict[str, Any]:
        """
        Evaluate relation extraction
        
        Args:
            predicted_path: Path to predicted relations JSON
            entities_path: Path to entities JSON
            ground_truth_path: Path to ground truth relations (optional)
            
        Returns:
            Evaluation metrics dictionary
        """
        predicted = self._load_json(predicted_path)
        entities = self._load_json(entities_path)
        
        # Schema compliance check
        schema_compliance = self._check_relation_schema_compliance(predicted)
        
        # Logical consistency check
        consistency = self._check_logical_consistency(predicted, entities)
        
        # Statistics
        statistics = self._compute_relation_statistics(predicted)
        
        # If ground truth is provided, compute precision/recall/F1
        if ground_truth_path:
            ground_truth = self._load_json(ground_truth_path)
            performance = self._compute_relation_performance(predicted, ground_truth)
        else:
            performance = {
                "precision": None,
                "recall": None,
                "f1_score": None,
                "note": "Ground truth not provided"
            }
        
        return {
            "schema_compliance": schema_compliance,
            "logical_consistency": consistency,
            "statistics": statistics,
            "performance": performance
        }
    
    def _check_entity_schema_compliance(self, entities: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Check if entities comply with schema"""
        compliance_report = {
            "compliant": True,
            "coverage": 0.0,
            "issues": [],
            "details": {}
        }
        
        # Check if all expected entity types are present
        expected_types = set(self.entities_schema.keys())
        actual_types = set(entities.keys())
        
        missing_types = expected_types - actual_types
        extra_types = actual_types - expected_types
        
        if missing_types:
            compliance_report["issues"].append(f"Missing entity types: {missing_types}")
            compliance_report["compliant"] = False
        
        if extra_types:
            compliance_report["issues"].append(f"Unexpected entity types: {extra_types}")
        
        # Check attribute compliance for each entity type
        for entity_type, expected_attrs in self.entities_schema.items():
            if entity_type not in entities:
                continue
            
            type_compliance = {
                "expected_attributes": expected_attrs,
                "compliant_count": 0,
                "total_count": len(entities[entity_type]),
                "attribute_issues": []
            }
            
            for entity in entities[entity_type]:
                actual_attrs = set(entity.keys())
                expected_attrs_set = set(expected_attrs)
                
                missing_attrs = expected_attrs_set - actual_attrs
                
                if not missing_attrs:
                    type_compliance["compliant_count"] += 1
                else:
                    type_compliance["attribute_issues"].append({
                        "entity": entity,
                        "missing_attributes": list(missing_attrs)
                    })
            
            # Limit reported issues
            if len(type_compliance["attribute_issues"]) > 5:
                type_compliance["attribute_issues"] = type_compliance["attribute_issues"][:5] + \
                    [{"note": f"... and {len(type_compliance['attribute_issues']) - 5} more issues"}]
            
            type_compliance["compliance_rate"] = type_compliance["compliant_count"] / max(type_compliance["total_count"], 1)
            compliance_report["details"][entity_type] = type_compliance
        
        # Calculate overall coverage
        total_types = len(expected_types)
        covered_types = len(expected_types & actual_types)
        compliance_report["coverage"] = covered_types / total_types if total_types > 0 else 0.0
        
        return compliance_report
    
    def _check_relation_schema_compliance(self, relations: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Check if relations comply with schema"""
        compliance_report = {
            "compliant": True,
            "coverage": 0.0,
            "issues": [],
            "details": {}
        }
        
        # Build expected relation types
        expected_types = {rel["name"] for rel in self.relations_schema["relations"]}
        actual_types = set(relations.keys())
        
        missing_types = expected_types - actual_types
        extra_types = actual_types - expected_types
        
        if missing_types:
            compliance_report["issues"].append(f"Missing relation types: {list(missing_types)[:10]}")
        
        if extra_types:
            compliance_report["issues"].append(f"Unexpected relation types: {extra_types}")
            compliance_report["compliant"] = False
        
        # Calculate coverage
        total_types = len(expected_types)
        covered_types = len(expected_types & actual_types)
        compliance_report["coverage"] = covered_types / total_types if total_types > 0 else 0.0
        
        return compliance_report
    
    def _check_logical_consistency(self, relations: Dict[str, List[Dict]], 
                                   entities: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Check logical consistency between relations and entities"""
        consistency_report = {
            "consistent": True,
            "issues": []
        }
        
        # Build entity lookup maps
        entity_names = defaultdict(set)
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                # Get the primary identifier (usually 'name')
                name = entity.get('name') or entity.get('title')
                if name:
                    entity_names[entity_type].add(name)
        
        # Check if relation entities exist
        for relation_type, relation_list in relations.items():
            for relation in relation_list:
                # Find the relation schema
                relation_schema = next((r for r in self.relations_schema["relations"] if r["name"] == relation_type), None)
                
                if not relation_schema:
                    continue
                
                # Check source entity
                source_entity_type = relation_schema.get("source_entity")
                target_entity_type = relation_schema.get("target_entity")
                
                # Get entity names from relation
                source_name = None
                target_name = None
                
                for key, value in relation.items():
                    if source_entity_type and source_entity_type.lower() in key.lower():
                        source_name = value
                    if target_entity_type and target_entity_type.lower() in key.lower():
                        target_name = value
                
                # Verify existence (relaxed check)
                # Note: This is a simplified check; in practice, you might want more sophisticated matching
        
        return consistency_report
    
    def _compute_entity_statistics(self, entities: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Compute entity extraction statistics"""
        stats = {
            "total_entities": 0,
            "by_type": {},
            "attribute_completeness": {}
        }
        
        for entity_type, entity_list in entities.items():
            count = len(entity_list)
            stats["total_entities"] += count
            stats["by_type"][entity_type] = count
            
            # Calculate attribute completeness
            if entity_type in self.entities_schema:
                expected_attrs = self.entities_schema[entity_type]
                complete_count = 0
                
                for entity in entity_list:
                    if all(attr in entity and entity[attr] for attr in expected_attrs):
                        complete_count += 1
                
                completeness = complete_count / count if count > 0 else 0.0
                stats["attribute_completeness"][entity_type] = f"{completeness:.2%}"
        
        return stats
    
    def _compute_relation_statistics(self, relations: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Compute relation extraction statistics"""
        stats = {
            "total_relations": 0,
            "by_type": {}
        }
        
        for relation_type, relation_list in relations.items():
            count = len(relation_list)
            stats["total_relations"] += count
            stats["by_type"][relation_type] = count
        
        return stats
    
    def _compute_entity_performance(self, predicted: Dict, ground_truth: Dict) -> Dict[str, float]:
        """Compute precision, recall, F1 for entity extraction"""
        total_tp = 0
        total_fp = 0
        total_fn = 0
        
        by_type = {}
        
        for entity_type in set(predicted.keys()) | set(ground_truth.keys()):
            pred_entities = set(self._entity_to_tuple(e) for e in predicted.get(entity_type, []))
            true_entities = set(self._entity_to_tuple(e) for e in ground_truth.get(entity_type, []))
            
            tp = len(pred_entities & true_entities)
            fp = len(pred_entities - true_entities)
            fn = len(true_entities - pred_entities)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            by_type[entity_type] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4)
            }
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
        
        # Overall metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "by_type": by_type
        }
    
    def _compute_relation_performance(self, predicted: Dict, ground_truth: Dict) -> Dict[str, float]:
        """Compute precision, recall, F1 for relation extraction"""
        total_tp = 0
        total_fp = 0
        total_fn = 0
        
        by_type = {}
        
        for relation_type in set(predicted.keys()) | set(ground_truth.keys()):
            pred_relations = set(self._relation_to_tuple(r) for r in predicted.get(relation_type, []))
            true_relations = set(self._relation_to_tuple(r) for r in ground_truth.get(relation_type, []))
            
            tp = len(pred_relations & true_relations)
            fp = len(pred_relations - true_relations)
            fn = len(true_relations - pred_relations)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            by_type[relation_type] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4)
            }
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
        
        # Overall metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "by_type": by_type
        }
    
    def _entity_to_tuple(self, entity: Dict) -> Tuple:
        """Convert entity to tuple for comparison"""
        # Use name as primary key
        return tuple(sorted(entity.items()))
    
    def _relation_to_tuple(self, relation: Dict) -> Tuple:
        """Convert relation to tuple for comparison"""
        # Use core fields only (exclude dates and metadata)
        core_fields = {k: v for k, v in relation.items() 
                      if k not in ["start_date", "end_date", "join_date", "appointment_date", 
                                  "establishment_date", "adoption_date", "tenure", "promotion_date"]}
        return tuple(sorted(core_fields.items()))
    
    def generate_report(self, 
                       method_name: str,
                       entities_predicted: str,
                       relations_predicted: str,
                       entities_ground_truth: str = None,
                       relations_ground_truth: str = None,
                       output_path: str = "output/evaluation_report.json") -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report
        
        Args:
            method_name: Name of the extraction method
            entities_predicted: Path to predicted entities
            relations_predicted: Path to predicted relations
            entities_ground_truth: Path to ground truth entities (optional)
            relations_ground_truth: Path to ground truth relations (optional)
            output_path: Path to save the report
            
        Returns:
            Evaluation report dictionary
        """
        entity_eval = self.evaluate_entities(entities_predicted, entities_ground_truth)
        relation_eval = self.evaluate_relations(relations_predicted, entities_predicted, relations_ground_truth)
        
        report = {
            "method": method_name,
            "timestamp": datetime.now().isoformat(),
            "entity_evaluation": {
                "schema_compliance": f"{entity_eval['schema_compliance']['coverage']:.2%}",
                "total_entities": entity_eval["statistics"]["total_entities"],
                "f1_score": entity_eval["performance"]["f1_score"],
                "precision": entity_eval["performance"]["precision"],
                "recall": entity_eval["performance"]["recall"],
                "details": entity_eval
            },
            "relation_evaluation": {
                "schema_compliance": f"{relation_eval['schema_compliance']['coverage']:.2%}",
                "total_relations": relation_eval["statistics"]["total_relations"],
                "f1_score": relation_eval["performance"]["f1_score"],
                "precision": relation_eval["performance"]["precision"],
                "recall": relation_eval["performance"]["recall"],
                "logical_consistency": relation_eval["logical_consistency"],
                "details": relation_eval
            }
        }
        
        # Save report
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nEvaluation report saved to {output_path}")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print(f"KGEB Evaluation Report: {report['method']}")
        print("="*60)
        
        print("\n📊 Entity Extraction:")
        entity_eval = report["entity_evaluation"]
        print(f"  Total Entities: {entity_eval['total_entities']}")
        print(f"  Schema Compliance: {entity_eval['schema_compliance']}")
        if entity_eval["f1_score"] is not None:
            print(f"  F1 Score: {entity_eval['f1_score']:.4f}")
            print(f"  Precision: {entity_eval['precision']:.4f}")
            print(f"  Recall: {entity_eval['recall']:.4f}")
        
        print("\n🔗 Relation Extraction:")
        relation_eval = report["relation_evaluation"]
        print(f"  Total Relations: {relation_eval['total_relations']}")
        print(f"  Schema Compliance: {relation_eval['schema_compliance']}")
        if relation_eval["f1_score"] is not None:
            print(f"  F1 Score: {relation_eval['f1_score']:.4f}")
            print(f"  Precision: {relation_eval['precision']:.4f}")
            print(f"  Recall: {relation_eval['recall']:.4f}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Example usage
    evaluator = KGEBEvaluator()
    
    # Generate report (without ground truth for demonstration)
    report = evaluator.generate_report(
        method_name="KGEB Baseline Method",
        entities_predicted="output/entities_output.json",
        relations_predicted="output/relations_output.json"
    )
    
    evaluator.print_summary(report)
