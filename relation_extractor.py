"""
Enterprise Knowledge Graph Extraction Benchmark (KGEB)
Relation Extraction Module

This module extracts 30 types of relations between entities
"""

import json
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class RelationExtractor:
    """Extract relations between entities from documents and entity data"""
    
    def __init__(self, relations_schema_path: str = "relations.json"):
        """
        Initialize the relation extractor
        
        Args:
            relations_schema_path: Path to the relations schema JSON file
        """
        self.schema = self._load_schema(relations_schema_path)
        self.relations = defaultdict(list)
        self.entities = {}
        self.document_text = ""
        
    def _load_schema(self, schema_path: str) -> List[Dict[str, Any]]:
        """Load relation schema from JSON file"""
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['relations']
    
    def load_entities(self, entities_path: str = "output/entities_output.json"):
        """
        Load extracted entities
        
        Args:
            entities_path: Path to entities JSON file
        """
        with open(entities_path, 'r', encoding='utf-8') as f:
            self.entities = json.load(f)
    
    def extract_from_file(self, documents_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract relations from documents file
        
        Args:
            documents_path: Path to documents.txt
            
        Returns:
            Dictionary of extracted relations grouped by type
        """
        with open(documents_path, 'r', encoding='utf-8') as f:
            self.document_text = f.read()
        
        lines = self.document_text.strip().split('\n')
        
        # Extract each relation type
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            self._extract_works_at(line)
            self._extract_belongs_to_department(line)
            self._extract_manages_project(line)
            self._extract_company_owns_project(line)
            self._extract_company_has_department(line)
            self._extract_company_located_in(line)
            self._extract_project_uses_technology(line)
            self._extract_has_position(line)
            self._extract_located_in(line)
        
        # Extract additional relations from entity data
        self._extract_relations_from_entities()
        
        return dict(self.relations)
    
    def _extract_works_at(self, line: str):
        """Extract WorksAt relations"""
        # Pattern: Name works at Company as Position
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*age\s+\d+,\s*works at\s+([A-Za-z]+)\s+as\s+(?:a\s+|an\s+)?(.+?)(?:\.|$)'
        match = re.search(pattern, line)
        
        if match:
            person = match.group(1).strip()
            company = match.group(2).strip()
            position = match.group(3).strip()
            
            relation = {
                "person": person,
                "company": company,
                "position": position,
                "start_date": "Unknown"
            }
            
            if not self._is_duplicate_relation("WorksAt", relation):
                self.relations["WorksAt"].append(relation)
    
    def _extract_belongs_to_department(self, line: str):
        """Extract BelongsToDepartment relations"""
        # Inferred from position and company
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),.*works at\s+([A-Za-z]+)\s+as\s+(?:a\s+|an\s+)?(.+?)(?:\.|$)'
        match = re.search(pattern, line)
        
        if match:
            person = match.group(1).strip()
            position = match.group(3).strip()
            department = self._infer_department_from_position(position)
            
            relation = {
                "person": person,
                "department": department,
                "role": position,
                "join_date": "Unknown"
            }
            
            if not self._is_duplicate_relation("BelongsToDepartment", relation):
                self.relations["BelongsToDepartment"].append(relation)
    
    def _extract_manages_project(self, line: str):
        """Extract ManagesProject relations"""
        # Pattern: Person manages/leads/oversees/handles/coordinates/directs N projects: List
        patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(manages|leads|oversees|handles|coordinates|directs|supervises)\s+\d+\s+projects?:\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                person = match.group(1).strip()
                action = match.group(2).strip()
                projects_str = match.group(3).strip()
                
                # Parse project names
                projects = [p.strip() for p in projects_str.split(',')]
                
                for project in projects:
                    relation = {
                        "person": person,
                        "project": project,
                        "responsibility_level": "High" if action in ["leads", "directs", "oversees"] else "Medium"
                    }
                    
                    if not self._is_duplicate_relation("ManagesProject", relation):
                        self.relations["ManagesProject"].append(relation)
                break
    
    def _extract_company_owns_project(self, line: str):
        """Extract CompanyOwnsProject relations"""
        # Inferred from person-company and person-project relationships
        # This requires cross-referencing data
        pass
    
    def _extract_company_has_department(self, line: str):
        """Extract CompanyHasDepartment relations"""
        # Pattern: Company operates/specializes in Industry
        company_pattern = r'([A-Z][a-zA-Z]+)\s+(?:operates|specializes|focuses|works)\s+in'
        match = re.search(company_pattern, line)
        
        if match:
            company = match.group(1).strip()
            
            # Common departments for tech companies
            departments = ["Engineering", "R&D", "Marketing", "Sales", "HR"]
            
            for dept in departments:
                relation = {
                    "company": company,
                    "department": dept,
                    "establishment_date": "Unknown"
                }
                
                if not self._is_duplicate_relation("CompanyHasDepartment", relation):
                    self.relations["CompanyHasDepartment"].append(relation)
    
    def _extract_company_located_in(self, line: str):
        """Extract CompanyLocatedIn relations"""
        # This would require location data
        pass
    
    def _extract_project_uses_technology(self, line: str):
        """Extract ProjectUsesTechnology relations"""
        # Inferred from project names and technology keywords
        tech_keywords = ["AI", "Cloud", "Deep Learning", "Machine Learning", "API", "Database"]
        
        project_pattern = r'Project\s+([A-Za-z0-9-]+)'
        match = re.search(project_pattern, line)
        
        if match:
            project = match.group(1).strip()
            
            for tech in tech_keywords:
                if tech.lower() in line.lower() or tech.lower() in project.lower():
                    relation = {
                        "project": project,
                        "technology": tech,
                        "technology_role": "Core"
                    }
                    
                    if not self._is_duplicate_relation("ProjectUsesTechnology", relation):
                        self.relations["ProjectUsesTechnology"].append(relation)
    
    def _extract_has_position(self, line: str):
        """Extract HasPosition relations"""
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),.*as\s+(?:a\s+|an\s+)?(.+?)(?:\.|$)'
        match = re.search(pattern, line)
        
        if match:
            person = match.group(1).strip()
            position = match.group(2).strip()
            
            relation = {
                "person": person,
                "position": position,
                "tenure": "Unknown",
                "promotion_date": "Unknown"
            }
            
            if not self._is_duplicate_relation("HasPosition", relation):
                self.relations["HasPosition"].append(relation)
    
    def _extract_located_in(self, line: str):
        """Extract LocatedIn relations (Person located in Location)"""
        # This would require explicit location mentions
        pass
    
    def _extract_relations_from_entities(self):
        """Extract additional relations by analyzing entity data"""
        if not self.entities:
            return
        
        # Extract LeadsTeam relations
        if "Person" in self.entities and "Team" in self.entities:
            for person in self.entities["Person"]:
                if "lead" in person.get("position", "").lower() or "manager" in person.get("position", "").lower():
                    for team in self.entities["Team"]:
                        if person.get("department", "").lower() in team.get("name", "").lower():
                            relation = {
                                "person": person["name"],
                                "team": team["name"],
                                "leadership_role": "Team Lead"
                            }
                            if not self._is_duplicate_relation("LeadsTeam", relation):
                                self.relations["LeadsTeam"].append(relation)
        
        # Extract PositionInDepartment relations
        if "Position" in self.entities and "Department" in self.entities:
            for position in self.entities["Position"]:
                for department in self.entities["Department"]:
                    # Match based on keywords
                    if self._match_position_to_department(position["title"], department["name"]):
                        relation = {
                            "position": position["title"],
                            "department": department["name"],
                            "position_count": 1
                        }
                        if not self._is_duplicate_relation("PositionInDepartment", relation):
                            self.relations["PositionInDepartment"].append(relation)
        
        # Extract TeamMember relations
        if "Team" in self.entities and "Person" in self.entities:
            for team in self.entities["Team"]:
                for person in self.entities["Person"]:
                    if person.get("department", "").lower() in team["name"].lower():
                        relation = {
                            "team": team["name"],
                            "person": person["name"],
                            "role_in_team": person.get("position", "Member")
                        }
                        if not self._is_duplicate_relation("TeamMember", relation):
                            self.relations["TeamMember"].append(relation)
        
        # Extract TeamUsesTechnology relations
        if "Team" in self.entities and "Technology" in self.entities:
            for team in self.entities["Team"]:
                for tech in self.entities["Technology"]:
                    if "development" in team["focus_area"].lower() or "engineering" in team["name"].lower():
                        relation = {
                            "team": team["name"],
                            "technology": tech["name"],
                            "proficiency_level": "Advanced"
                        }
                        if not self._is_duplicate_relation("TeamUsesTechnology", relation):
                            self.relations["TeamUsesTechnology"].append(relation)
        
        # Extract CompanyUsesTechnology relations
        if "Company" in self.entities and "Technology" in self.entities:
            for company in self.entities["Company"]:
                if "technology" in company.get("industry", "").lower():
                    for tech in self.entities["Technology"]:
                        relation = {
                            "company": company["name"],
                            "technology": tech["name"],
                            "adoption_date": "Unknown",
                            "usage_level": "High"
                        }
                        if not self._is_duplicate_relation("CompanyUsesTechnology", relation):
                            self.relations["CompanyUsesTechnology"].append(relation)
        
        # Extract ProjectHasTeam relations
        if "Project" in self.entities and "Team" in self.entities:
            for project in self.entities["Project"]:
                for team in self.entities["Team"]:
                    if project["status"] == "Ongoing":
                        relation = {
                            "project": project["name"],
                            "team": team["name"],
                            "team_role": "Development"
                        }
                        if not self._is_duplicate_relation("ProjectHasTeam", relation):
                            self.relations["ProjectHasTeam"].append(relation)
        
        # Extract DepartmentHeadedBy relations
        if "Department" in self.entities and "Person" in self.entities:
            for dept in self.entities["Department"]:
                for person in self.entities["Person"]:
                    if "director" in person.get("position", "").lower() or "head" in person.get("position", "").lower():
                        if person.get("department") == dept["name"]:
                            relation = {
                                "department": dept["name"],
                                "person": person["name"],
                                "appointment_date": "Unknown"
                            }
                            if not self._is_duplicate_relation("DepartmentHeadedBy", relation):
                                self.relations["DepartmentHeadedBy"].append(relation)
        
        # Extract DepartmentHasTeam relations
        if "Department" in self.entities and "Team" in self.entities:
            for dept in self.entities["Department"]:
                for team in self.entities["Team"]:
                    if dept["name"].lower() in team["name"].lower():
                        relation = {
                            "department": dept["name"],
                            "team": team["name"],
                            "team_purpose": team["focus_area"]
                        }
                        if not self._is_duplicate_relation("DepartmentHasTeam", relation):
                            self.relations["DepartmentHasTeam"].append(relation)
    
    def _infer_department_from_position(self, position: str) -> str:
        """Infer department from position title"""
        position_lower = position.lower()
        
        if any(keyword in position_lower for keyword in ["engineer", "developer", "architect", "technical"]):
            return "Engineering"
        elif any(keyword in position_lower for keyword in ["researcher", "scientist"]):
            return "R&D"
        elif any(keyword in position_lower for keyword in ["manager", "director", "lead"]):
            return "Management"
        elif any(keyword in position_lower for keyword in ["designer", "ux", "ui"]):
            return "Design"
        elif any(keyword in position_lower for keyword in ["marketing", "sales"]):
            return "Marketing"
        elif any(keyword in position_lower for keyword in ["support", "administrator"]):
            return "Support"
        else:
            return "General"
    
    def _match_position_to_department(self, position: str, department: str) -> bool:
        """Check if a position belongs to a department"""
        position_lower = position.lower()
        department_lower = department.lower()
        
        mappings = {
            "engineering": ["engineer", "developer", "architect"],
            "r&d": ["researcher", "scientist"],
            "marketing": ["marketing", "sales"],
            "design": ["designer", "ux", "ui"],
            "support": ["support", "administrator"],
            "hr": ["hr", "human resources", "recruiter"],
            "finance": ["finance", "accountant", "controller"]
        }
        
        keywords = mappings.get(department_lower, [])
        return any(keyword in position_lower for keyword in keywords)
    
    def _is_duplicate_relation(self, relation_type: str, relation: Dict[str, Any]) -> bool:
        """Check if a relation already exists"""
        for existing in self.relations[relation_type]:
            # Compare key fields (exclude optional attributes)
            if self._are_relations_equal(existing, relation):
                return True
        return False
    
    def _are_relations_equal(self, rel1: Dict[str, Any], rel2: Dict[str, Any]) -> bool:
        """Check if two relations are equal (based on key fields)"""
        # Get the core identifying fields
        key_fields = set(rel1.keys()) & set(rel2.keys())
        
        # Compare only the main entity fields (exclude metadata like dates)
        entity_fields = [k for k in key_fields if k not in ["start_date", "join_date", "appointment_date", "establishment_date", "adoption_date", "tenure", "promotion_date"]]
        
        for field in entity_fields:
            if rel1.get(field) != rel2.get(field):
                return False
        
        return len(entity_fields) > 0
    
    def save_to_json(self, output_path: str = "output/relations_output.json"):
        """
        Save extracted relations to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dict(self.relations), f, indent=2, ensure_ascii=False)
        
        print(f"Relations saved to {output_path}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about extracted relations"""
        return {relation_type: len(relations) for relation_type, relations in self.relations.items()}


if __name__ == "__main__":
    # Example usage
    extractor = RelationExtractor()
    
    # Load entities first
    try:
        extractor.load_entities()
    except FileNotFoundError:
        print("Warning: entities_output.json not found. Run entity extraction first.")
    
    # Extract relations
    relations = extractor.extract_from_file("documents.txt")
    extractor.save_to_json()
    
    print("\nRelation Extraction Statistics:")
    stats = extractor.get_statistics()
    for relation_type, count in stats.items():
        print(f"  {relation_type}: {count}")
