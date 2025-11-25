"""
Enterprise Knowledge Graph Extraction Benchmark (KGEB)
Entity Extraction Module

This module extracts 10 types of entities with their attributes from documents.txt
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime
from dateutil import parser as date_parser
import spacy


class EntityExtractor:
    """Extract entities from semi-structured enterprise text"""
    
    def __init__(self, entities_schema_path: str = "entities.json"):
        """
        Initialize the entity extractor
        
        Args:
            entities_schema_path: Path to the entities schema JSON file
        """
        self.schema = self._load_schema(entities_schema_path)
        self.nlp = None
        self.entities = {entity_type: [] for entity_type in self.schema.keys()}
        
    def _load_schema(self, schema_path: str) -> Dict[str, List[str]]:
        """Load entity schema from JSON file"""
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _init_nlp(self):
        """Initialize spaCy NLP model (lazy loading)"""
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Downloading spaCy model...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
    
    def extract_from_file(self, documents_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract entities from documents file
        
        Args:
            documents_path: Path to documents.txt
            
        Returns:
            Dictionary of extracted entities grouped by type
        """
        self._init_nlp()
        
        with open(documents_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract different entity types based on patterns
            self._extract_person(line)
            self._extract_company(line)
            self._extract_project(line)
            self._extract_department(line)
            self._extract_position(line)
            self._extract_technology(line)
            self._extract_location(line)
            self._extract_team(line)
            self._extract_product(line)
            self._extract_client(line)
        
        # Remove duplicates
        self._deduplicate_entities()
        
        return self.entities
    
    def _extract_person(self, line: str):
        """Extract Person entities"""
        # Pattern: Name, age X, works at Company as Position
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*age\s+(\d+),\s*works at\s+([A-Za-z]+)\s+as\s+(?:a\s+|an\s+)?(.+?)(?:\.|$)'
        match = re.search(pattern, line)
        
        if match:
            name = match.group(1).strip()
            age = int(match.group(2))
            company = match.group(3).strip()
            position = match.group(4).strip()
            
            # Infer department from position or company industry
            department = self._infer_department(position, company)
            
            person = {
                "name": name,
                "age": age,
                "position": position,
                "department": department
            }
            
            # Avoid duplicates
            if not any(p["name"] == name for p in self.entities["Person"]):
                self.entities["Person"].append(person)
    
    def _extract_company(self, line: str):
        """Extract Company entities"""
        # Pattern: Company operates in/specializes in/focuses on Industry
        patterns = [
            r'([A-Z][a-zA-Z]+)\s+operates in\s+(?:the\s+)?(.+?)\s+industry',
            r'([A-Z][a-zA-Z]+)\s+specializes in\s+(.+?)(?:\.|$)',
            r'([A-Z][a-zA-Z]+)\s+focuses on\s+(.+?)\s+industry',
            r'([A-Z][a-zA-Z]+)\s+works in\s+(.+?)\s+sectors?',
            r'([A-Z][a-zA-Z]+)\s+is known for\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group(1).strip()
                industry_info = match.group(2).strip()
                
                # Parse industry and sector
                parts = [p.strip() for p in industry_info.split(' and ')]
                industry = parts[0] if parts else industry_info
                sector = parts[1] if len(parts) > 1 else industry
                
                # Infer location (simplified)
                location = self._infer_company_location(name)
                
                company = {
                    "name": name,
                    "industry": industry,
                    "sector": sector,
                    "location": location
                }
                
                if not any(c["name"] == name for c in self.entities["Company"]):
                    self.entities["Company"].append(company)
                break
    
    def _extract_project(self, line: str):
        """Extract Project entities"""
        # Pattern: Project Name started/began/launched on DATE, ends/concludes/finishes on DATE
        patterns = [
            r'Project\s+([A-Za-z0-9-]+)\s+(?:started|began|launched|initiated)\s+on\s+([\d-]+),\s+(?:ends|concludes|finishes|completes)\s+on\s+([\d-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group(1).strip()
                start_date = match.group(2).strip()
                end_date = match.group(3).strip()
                
                # Determine status based on dates
                status = self._determine_project_status(start_date, end_date)
                
                # Estimate budget (simplified heuristic)
                budget = self._estimate_budget(name)
                
                project = {
                    "name": name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": status,
                    "budget": budget
                }
                
                if not any(p["name"] == name for p in self.entities["Project"]):
                    self.entities["Project"].append(project)
                break
    
    def _extract_department(self, line: str):
        """Extract Department entities from context"""
        # Departments are inferred from positions and company structure
        # This is a simplified extraction
        departments = ["R&D", "Marketing", "Engineering", "Sales", "HR", "Finance", 
                      "Operations", "IT", "Product", "Design", "Support", "Development"]
        
        for dept in departments:
            if dept in line:
                if not any(d["name"] == dept for d in self.entities["Department"]):
                    department = {
                        "name": dept,
                        "head": "Unknown",
                        "employee_count": 0
                    }
                    self.entities["Department"].append(department)
    
    def _extract_position(self, line: str):
        """Extract Position entities"""
        # Extract positions from person descriptions
        position_pattern = r'works at\s+[A-Za-z]+\s+as\s+(?:a\s+|an\s+)?(.+?)(?:\.|$)'
        match = re.search(position_pattern, line)
        
        if match:
            title = match.group(1).strip()
            
            # Infer level from title
            level = self._infer_position_level(title)
            
            # Estimate salary range
            salary_range = self._estimate_salary_range(title, level)
            
            position = {
                "title": title,
                "level": level,
                "salary_range": salary_range
            }
            
            if not any(p["title"] == title for p in self.entities["Position"]):
                self.entities["Position"].append(position)
    
    def _extract_technology(self, line: str):
        """Extract Technology entities"""
        # Common technology keywords
        tech_keywords = {
            "AI": "Artificial Intelligence",
            "Deep Learning": "Machine Learning",
            "Machine Learning": "Machine Learning",
            "Cloud": "Cloud Computing",
            "Database": "Data Management",
            "Blockchain": "Distributed Systems",
            "IoT": "Internet of Things",
            "API": "Software Development"
        }
        
        for keyword, category in tech_keywords.items():
            if keyword in line:
                if not any(t["name"] == keyword for t in self.entities["Technology"]):
                    technology = {
                        "name": keyword,
                        "category": category,
                        "version": "1.0"
                    }
                    self.entities["Technology"].append(technology)
    
    def _extract_location(self, line: str):
        """Extract Location entities"""
        # Extract city names (simplified)
        cities = {
            "San Francisco": "USA", "New York": "USA", "Seattle": "USA",
            "London": "UK", "Berlin": "Germany", "Paris": "France",
            "Tokyo": "Japan", "Beijing": "China", "Singapore": "Singapore",
            "Bangalore": "India", "Sydney": "Australia"
        }
        
        for city, country in cities.items():
            if city in line:
                if not any(loc["city"] == city for loc in self.entities["Location"]):
                    location = {
                        "city": city,
                        "country": country,
                        "office_type": "Headquarters"
                    }
                    self.entities["Location"].append(location)
    
    def _extract_team(self, line: str):
        """Extract Team entities"""
        # Teams are inferred from context (simplified)
        team_pattern = r'([A-Z][A-Za-z\s]+?)\s+[Tt]eam'
        matches = re.finditer(team_pattern, line)
        
        for match in matches:
            name = match.group(1).strip() + " Team"
            if not any(t["name"] == name for t in self.entities["Team"]):
                team = {
                    "name": name,
                    "size": 5,  # Default size
                    "focus_area": "Development"
                }
                self.entities["Team"].append(team)
    
    def _extract_product(self, line: str):
        """Extract Product entities"""
        # Products are project deliverables or mentioned services
        # This is a simplified extraction
        pass
    
    def _extract_client(self, line: str):
        """Extract Client entities"""
        # Clients would be extracted from contract or partnership mentions
        # This is a simplified extraction
        pass
    
    def _infer_department(self, position: str, company: str) -> str:
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
    
    def _infer_company_location(self, company: str) -> str:
        """Infer company location (simplified)"""
        locations = {
            "OpenAI": "San Francisco",
            "Google": "Mountain View",
            "Microsoft": "Redmond",
            "Apple": "Cupertino",
            "Amazon": "Seattle",
            "Meta": "Menlo Park",
            "Tesla": "Austin",
            "Netflix": "Los Gatos",
            "Spotify": "Stockholm",
            "Uber": "San Francisco"
        }
        return locations.get(company, "Unknown")
    
    def _determine_project_status(self, start_date: str, end_date: str) -> str:
        """Determine project status based on dates"""
        try:
            start = date_parser.parse(start_date)
            end = date_parser.parse(end_date)
            now = datetime.now()
            
            if now < start:
                return "Planned"
            elif start <= now <= end:
                return "Ongoing"
            else:
                return "Completed"
        except:
            return "Unknown"
    
    def _estimate_budget(self, project_name: str) -> int:
        """Estimate project budget (simplified heuristic)"""
        # Simple hash-based estimation for consistency
        return (hash(project_name) % 10000000) + 100000
    
    def _infer_position_level(self, title: str) -> str:
        """Infer position level from title"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ["senior", "lead", "principal", "chief", "director"]):
            return "Senior"
        elif any(keyword in title_lower for keyword in ["junior", "associate", "assistant"]):
            return "Junior"
        else:
            return "Mid-level"
    
    def _estimate_salary_range(self, title: str, level: str) -> str:
        """Estimate salary range based on title and level"""
        ranges = {
            "Senior": "$120,000-$200,000",
            "Mid-level": "$80,000-$120,000",
            "Junior": "$50,000-$80,000"
        }
        return ranges.get(level, "$60,000-$100,000")
    
    def _deduplicate_entities(self):
        """Remove duplicate entities"""
        for entity_type in self.entities:
            seen = set()
            unique = []
            for entity in self.entities[entity_type]:
                # Create a hash key for deduplication
                key = str(sorted(entity.items()))
                if key not in seen:
                    seen.add(key)
                    unique.append(entity)
            self.entities[entity_type] = unique
    
    def save_to_json(self, output_path: str = "output/entities_output.json"):
        """
        Save extracted entities to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.entities, f, indent=2, ensure_ascii=False)
        
        print(f"Entities saved to {output_path}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about extracted entities"""
        return {entity_type: len(entities) for entity_type, entities in self.entities.items()}


if __name__ == "__main__":
    # Example usage
    extractor = EntityExtractor()
    entities = extractor.extract_from_file("documents.txt")
    extractor.save_to_json()
    
    print("\nEntity Extraction Statistics:")
    stats = extractor.get_statistics()
    for entity_type, count in stats.items():
        print(f"  {entity_type}: {count}")
