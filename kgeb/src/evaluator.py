"""
Evaluation Framework for KGEB
Evaluates entity and relation extraction methods
"""

import json
from typing import Dict, List, Any, Tuple
from datetime import datetime


class EvaluationMetrics:
    """Calculate evaluation metrics for extraction results"""
    
    @staticmethod
    def calculate_precision_recall_f1(
        predicted: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]],
        match_keys: List[str] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate precision, recall, and F1 score
        
        Args:
            predicted: Predicted items
            ground_truth: Ground truth items
            match_keys: Keys to use for matching (default: all keys)
        
        Returns:
            Tuple of (precision, recall, f1)
        """
        if not ground_truth:
            return 0.0, 0.0, 0.0
        
        if not match_keys:
            match_keys = list(ground_truth[0].keys()) if ground_truth else []
        
        # Convert to comparable format
        pred_set = set()
        for item in predicted:
            key_tuple = tuple(item.get(k, '') for k in match_keys)
            pred_set.add(key_tuple)
        
        truth_set = set()
        for item in ground_truth:
            key_tuple = tuple(item.get(k, '') for k in match_keys)
            truth_set.add(key_tuple)
        
        # Calculate TP, FP, FN
        tp = len(pred_set & truth_set)
        fp = len(pred_set - truth_set)
        fn = len(truth_set - pred_set)
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1
    
    @staticmethod
    def check_schema_compliance(
        entities: Dict[str, List[Dict[str, Any]]],
        schema: Dict[str, List[str]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Check if extracted entities comply with schema
        
        Args:
            entities: Extracted entities
            schema: Entity schema
        
        Returns:
            Tuple of (compliance_percentage, details)
        """
        total_attributes = 0
        compliant_attributes = 0
        details = {}
        
        for entity_type, instances in entities.items():
            if entity_type not in schema:
                continue
            
            expected_attrs = set(schema[entity_type])
            type_compliant = 0
            type_total = 0
            
            for instance in instances:
                instance_attrs = set(instance.keys())
                type_total += 1
                
                # Check if all expected attributes are present
                if expected_attrs.issubset(instance_attrs):
                    type_compliant += 1
                
                total_attributes += len(expected_attrs)
                compliant_attributes += len(expected_attrs & instance_attrs)
            
            if type_total > 0:
                details[entity_type] = {
                    "total_instances": type_total,
                    "compliant_instances": type_compliant,
                    "compliance_rate": type_compliant / type_total
                }
        
        compliance_percentage = (compliant_attributes / total_attributes * 100) if total_attributes > 0 else 0.0
        
        return compliance_percentage, details
    
    @staticmethod
    def check_logical_consistency(
        entities: Dict[str, List[Dict[str, Any]]],
        relations: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[float, List[str]]:
        """
        Check logical consistency between entities and relations
        
        Args:
            entities: Extracted entities
            relations: Extracted relations
        
        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        
        # Create entity lookup tables
        person_names = {p['name'] for p in entities.get('Person', []) if 'name' in p}
        company_names = {c['name'] for c in entities.get('Company', []) if 'name' in c}
        project_names = {p['name'] for p in entities.get('Project', []) if 'name' in p}
        
        # Check WorksAt relations
        for rel in relations.get('WorksAt', []):
            if rel.get('person') not in person_names:
                issues.append(f"WorksAt: Person '{rel.get('person')}' not found in Person entities")
            if rel.get('company') not in company_names:
                issues.append(f"WorksAt: Company '{rel.get('company')}' not found in Company entities")
        
        # Check ManagesProject relations
        for rel in relations.get('ManagesProject', []):
            if rel.get('person') not in person_names:
                issues.append(f"ManagesProject: Person '{rel.get('person')}' not found in Person entities")
            if rel.get('project') not in project_names:
                issues.append(f"ManagesProject: Project '{rel.get('project')}' not found in Project entities")
        
        # Check OwnsProject relations
        for rel in relations.get('OwnsProject', []):
            if rel.get('company') not in company_names:
                issues.append(f"OwnsProject: Company '{rel.get('company')}' not found in Company entities")
            if rel.get('project') not in project_names:
                issues.append(f"OwnsProject: Project '{rel.get('project')}' not found in Project entities")
        
        consistency_score = 1.0 - (len(issues) / max(1, len(relations) * 2))
        consistency_score = max(0.0, consistency_score)
        
        return consistency_score, issues


class Evaluator:
    """Evaluates extraction results against ground truth or predefined metrics"""
    
    def __init__(self, entities_schema: Dict[str, List[str]], relations_schema: Dict[str, Any]):
        """
        Initialize evaluator
        
        Args:
            entities_schema: Entity type schema
            relations_schema: Relation type schema
        """
        self.entities_schema = entities_schema
        self.relations_schema = relations_schema
        self.evaluation_results = {}
    
    def evaluate_entities(
        self,
        extracted_entities: Dict[str, List[Dict[str, Any]]],
        ground_truth_entities: Dict[str, List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate extracted entities
        
        Args:
            extracted_entities: Extracted entities from EntityExtractor
            ground_truth_entities: Ground truth entities (optional)
        
        Returns:
            Evaluation results
        """
        results = {}
        
        # Schema compliance check
        compliance_pct, compliance_details = EvaluationMetrics.check_schema_compliance(
            extracted_entities, self.entities_schema
        )
        results['schema_compliance'] = {
            'percentage': compliance_pct,
            'details': compliance_details
        }
        
        # If ground truth provided, calculate metrics
        if ground_truth_entities:
            entity_f1_scores = {}
            for entity_type in self.entities_schema:
                pred = extracted_entities.get(entity_type, [])
                truth = ground_truth_entities.get(entity_type, [])
                
                if truth:
                    precision, recall, f1 = EvaluationMetrics.calculate_precision_recall_f1(
                        pred, truth, match_keys=['name']
                    )
                    entity_f1_scores[entity_type] = {
                        'precision': precision,
                        'recall': recall,
                        'f1': f1
                    }
            
            # Calculate overall entity F1
            if entity_f1_scores:
                avg_f1 = sum(m['f1'] for m in entity_f1_scores.values()) / len(entity_f1_scores)
                results['entity_f1'] = avg_f1
                results['entity_metrics_by_type'] = entity_f1_scores
        
        return results
    
    def evaluate_relations(
        self,
        extracted_relations: Dict[str, List[Dict[str, Any]]],
        extracted_entities: Dict[str, List[Dict[str, Any]]],
        ground_truth_relations: Dict[str, List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate extracted relations
        
        Args:
            extracted_relations: Extracted relations
            extracted_entities: Extracted entities (for consistency check)
            ground_truth_relations: Ground truth relations (optional)
        
        Returns:
            Evaluation results
        """
        results = {}
        
        # Logical consistency check
        consistency_score, issues = EvaluationMetrics.check_logical_consistency(
            extracted_entities, extracted_relations
        )
        results['logical_consistency'] = {
            'score': consistency_score,
            'issues': issues[:10]  # First 10 issues
        }
        
        # If ground truth provided, calculate metrics
        if ground_truth_relations:
            relation_f1_scores = {}
            for rel_type in ground_truth_relations:
                pred = extracted_relations.get(rel_type, [])
                truth = ground_truth_relations.get(rel_type, [])
                
                if truth:
                    # Get all keys for matching
                    match_keys = list(truth[0].keys()) if truth else []
                    precision, recall, f1 = EvaluationMetrics.calculate_precision_recall_f1(
                        pred, truth, match_keys=match_keys
                    )
                    relation_f1_scores[rel_type] = {
                        'precision': precision,
                        'recall': recall,
                        'f1': f1
                    }
            
            # Calculate overall relation F1
            if relation_f1_scores:
                avg_f1 = sum(m['f1'] for m in relation_f1_scores.values()) / len(relation_f1_scores)
                results['relation_f1'] = avg_f1
                results['relation_metrics_by_type'] = relation_f1_scores
        
        return results
    
    def generate_report(
        self,
        entity_results: Dict[str, Any],
        relation_results: Dict[str, Any],
        method_name: str = "Unknown Method"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report
        
        Args:
            entity_results: Entity evaluation results
            relation_results: Relation evaluation results
            method_name: Name of the extraction method
        
        Returns:
            Complete evaluation report
        """
        report = {
            "method": method_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entity_evaluation": entity_results,
            "relation_evaluation": relation_results,
            "overall_metrics": {
                "entity_f1": entity_results.get('entity_f1', 0.0),
                "relation_f1": relation_results.get('relation_f1', 0.0),
                "schema_compliance": entity_results.get('schema_compliance', {}).get('percentage', 0.0),
                "logical_consistency": relation_results.get('logical_consistency', {}).get('score', 0.0)
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filepath: str) -> None:
        """Save evaluation report to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Evaluation report saved to {filepath}")


def main():
    """Main function for evaluation"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python evaluator.py <entities_file> <relations_file> [output_file]")
        sys.exit(1)
    
    entities_file = sys.argv[1]
    relations_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "evaluation_report.json"
    
    # Load schemas
    with open('../config/entities.json', 'r', encoding='utf-8') as f:
        entities_schema = json.load(f)
    
    with open('../config/relations.json', 'r', encoding='utf-8') as f:
        relations_schema = json.load(f)
    
    # Load extraction results
    with open(entities_file, 'r', encoding='utf-8') as f:
        extracted_entities = json.load(f)
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        extracted_relations = json.load(f)
    
    # Evaluate
    evaluator = Evaluator(entities_schema, relations_schema)
    
    entity_results = evaluator.evaluate_entities(extracted_entities)
    relation_results = evaluator.evaluate_relations(extracted_relations, extracted_entities)
    
    report = evaluator.generate_report(entity_results, relation_results, method_name="KGEB Extraction Pipeline")
    
    # Save report
    evaluator.save_report(report, output_file)
    
    # Print summary
    print("\nEvaluation Summary:")
    print(f"Entity F1: {report['overall_metrics']['entity_f1']:.2%}")
    print(f"Relation F1: {report['overall_metrics']['relation_f1']:.2%}")
    print(f"Schema Compliance: {report['overall_metrics']['schema_compliance']:.2%}")
    print(f"Logical Consistency: {report['overall_metrics']['logical_consistency']:.2%}")


if __name__ == "__main__":
    main()
