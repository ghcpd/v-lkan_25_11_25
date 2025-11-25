"""
Relation Extraction Module for KGEB
Extracts relationships between entities from semi-structured text
"""

import json
import re
from typing import Dict, List, Any, Tuple


class RelationExtractor:
    """Extracts relations between entities from enterprise documents"""
    
    def __init__(self, relations_schema: Dict[str, Any], entities: Dict[str, List[Dict[str, Any]]]):
        """
        Initialize relation extractor
        
        Args:
            relations_schema: Dictionary defining relation types
            entities: Extracted entities from entity extractor
        """
        self.schema = relations_schema.get('relation_types', [])
        self.entities = entities
        self.extracted_relations = {}
        self._init_relations_dict()
    
    def _init_relations_dict(self) -> None:
        """Initialize extracted relations dictionary"""
        for rel_type in self.schema:
            self.extracted_relations[rel_type['name']] = []
    
    def extract_belongs_to(self, text: str) -> List[Dict[str, Any]]:
        """Extract BelongsTo relations (Person -> Department)"""
        relations = []
        # Pattern: Name manages/leads X projects
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:manages|leads|oversees|supervises|handles|coordinates|directs)\s+(\d+)\s+projects?'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person_name = match.group(1).strip()
            # Find matching person
            for person in self.entities.get('Person', []):
                if person['name'] == person_name:
                    relations.append({
                        "person": person_name,
                        "department": person.get('department', 'Unknown')
                    })
                    break
        
        return relations
    
    def extract_works_at(self, text: str) -> List[Dict[str, Any]]:
        """Extract WorksAt relations (Person -> Company)"""
        relations = []
        # Pattern: Name, age N, works at Company
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+),\s*age\s*\d+,\s*works\s+at\s+([A-Za-z0-9&\s]+?)\s+as'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person_name = match.group(1).strip()
            company_name = match.group(2).strip()
            
            relations.append({
                "person": person_name,
                "company": company_name,
                "employment_type": "Full-time"
            })
        
        return relations
    
    def extract_has_position(self, text: str) -> List[Dict[str, Any]]:
        """Extract HasPosition relations (Person -> Position)"""
        relations = []
        # Pattern: Name works as Position
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+).*?as\s+(?:an?\s+)?([A-Za-z\s]+)\.'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person_name = match.group(1).strip()
            position_title = match.group(2).strip()
            
            relations.append({
                "person": person_name,
                "position": position_title,
                "status": "Active"
            })
        
        return relations
    
    def extract_manages_project(self, text: str) -> List[Dict[str, Any]]:
        """Extract ManagesProject relations (Person -> Project)"""
        relations = []
        # Pattern: Name manages/leads/oversees X projects: Project1, Project2, ...
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:manages|leads|oversees|supervises|handles|coordinates|directs)\s+(\d+)\s+projects?:\s+([A-Za-z0-9\s,\-]+)\.'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person_name = match.group(1).strip()
            projects_text = match.group(3).strip()
            projects = [p.strip() for p in projects_text.split(',')]
            
            for project in projects:
                project = project.strip()
                if project:
                    relations.append({
                        "person": person_name,
                        "project": project,
                        "role": "Manager"
                    })
        
        return relations
    
    def extract_owns_project(self, text: str) -> List[Dict[str, Any]]:
        """Extract OwnsProject relations (Company -> Project)"""
        relations = []
        # Companies own projects - infer from person-project-company relationships
        person_projects = self.extract_manages_project(text)
        works_at = self.extract_works_at(text)
        
        person_company_map = {}
        for rel in works_at:
            person_company_map[rel['person']] = rel['company']
        
        for person_proj in person_projects:
            if person_proj['person'] in person_company_map:
                relations.append({
                    "company": person_company_map[person_proj['person']],
                    "project": person_proj['project'],
                    "status": "Active"
                })
        
        return relations
    
    def extract_operates_in(self, text: str) -> List[Dict[str, Any]]:
        """Extract OperatesIn relations (Company -> Location)"""
        relations = []
        # Pattern: Company located in City
        pattern = r'((?:Shenzhen|Hangzhou|Beijing|Shanghai|San Francisco|New York|London|Tokyo))'
        cities = set(re.findall(pattern, text))
        
        # Map some known companies to cities
        city_company_map = {
            "Shenzhen": ["Tencent"],
            "Hangzhou": ["Alibaba"],
            "Beijing": ["ByteDance"],
            "Shanghai": [],
        }
        
        for city in cities:
            for company in city_company_map.get(city, []):
                relations.append({
                    "company": company,
                    "location": city,
                    "office_type": "Headquarters"
                })
        
        return relations
    
    def extract_produces_product(self, text: str) -> List[Dict[str, Any]]:
        """Extract ProducesProduct relations (Company -> Product)"""
        relations = []
        # Pattern: Company produces Product
        pattern = r'([A-Za-z0-9&\s]+?)\s+produces\s+(?:a\s+)?([A-Za-z0-9\s\-]+?)[\.,]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            company_name = match.group(1).strip()
            product_name = match.group(2).strip()
            
            relations.append({
                "company": company_name,
                "product": product_name,
                "status": "Active"
            })
        
        return relations
    
    def extract_uses_technology(self, text: str) -> List[Dict[str, Any]]:
        """Extract UsesTechnology relations (Team/Project -> Technology)"""
        relations = []
        # Pattern: Team/Project uses Technology
        pattern = r'([A-Za-z0-9\s]+?)\s+uses\s+([A-Za-z0-9\s]+?)[\.,]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            entity_name = match.group(1).strip()
            technology_name = match.group(2).strip()
            
            if "Team" in entity_name or "Project" in entity_name:
                relations.append({
                    "entity": entity_name,
                    "technology": technology_name,
                    "adoption_date": "2024-01-01"
                })
        
        return relations
    
    def extract_contributes(self, text: str) -> List[Dict[str, Any]]:
        """Extract Contributes relations (Person -> Project)"""
        relations = []
        # Pattern: Person contributes to Project
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+).*?(?:contributes to|works on)\s+([A-Za-z0-9\-\s]+?)[\.,]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person_name = match.group(1).strip()
            project_name = match.group(2).strip()
            
            relations.append({
                "person": person_name,
                "project": project_name,
                "contribution_type": "Development"
            })
        
        return relations
    
    def extract_all(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all relation types from text"""
        self.extracted_relations = {
            "BelongsTo": self.extract_belongs_to(text),
            "WorksAt": self.extract_works_at(text),
            "HasPosition": self.extract_has_position(text),
            "ManagesProject": self.extract_manages_project(text),
            "OwnsProject": self.extract_owns_project(text),
            "OperatesIn": self.extract_operates_in(text),
            "ProducesProduct": self.extract_produces_product(text),
            "UsesTechnology": self.extract_uses_technology(text),
            "Contributes": self.extract_contributes(text),
        }
        return self.extracted_relations
    
    def to_json(self) -> str:
        """Convert extracted relations to JSON format"""
        return json.dumps(self.extracted_relations, indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """Save extracted relations to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_relations, f, indent=2, ensure_ascii=False)
        print(f"Relations saved to {filepath}")


def main():
    """Main function for relation extraction"""
    import sys
    from entity_extractor import EntityExtractor
    
    if len(sys.argv) < 2:
        print("Usage: python relation_extractor.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "relations_output.json"
    
    # Load schemas
    with open('../config/relations.json', 'r', encoding='utf-8') as f:
        relations_schema = json.load(f)
    
    # Read input document
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # First extract entities
    entities_schema = {
        "Person": ["name", "age", "position", "department"],
        "Company": ["name", "industry", "sector", "location"],
        "Project": ["name", "start_date", "end_date", "status", "budget"],
        "Department": ["name", "head", "employee_count"],
        "Position": ["title", "level", "salary_range"],
        "Technology": ["name", "category", "version"],
        "Location": ["city", "country", "office_type"],
        "Team": ["name", "size", "focus_area"],
        "Product": ["name", "version", "release_date"],
        "Client": ["name", "contract_value", "industry"],
    }
    
    entity_extractor = EntityExtractor(entities_schema)
    entities = entity_extractor.extract_all(text)
    
    # Extract relations
    extractor = RelationExtractor(relations_schema, entities)
    relations = extractor.extract_all(text)
    
    # Save output
    extractor.save_to_file(output_file)
    
    # Print summary
    print("\nRelation Extraction Summary:")
    for relation_type, items in relations.items():
        print(f"{relation_type}: {len(items)} relations found")


if __name__ == "__main__":
    main()
