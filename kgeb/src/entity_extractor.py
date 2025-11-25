"""
Entity Extraction Module for KGEB
Extracts entities from semi-structured enterprise text
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime


class EntityExtractor:
    """Extracts entities from enterprise documents"""
    
    def __init__(self, entities_schema: Dict[str, List[str]]):
        """
        Initialize entity extractor with schema
        
        Args:
            entities_schema: Dictionary defining entity types and their attributes
        """
        self.schema = entities_schema
        self.extracted_entities = {entity_type: [] for entity_type in entities_schema.keys()}
    
    def extract_persons(self, text: str) -> List[Dict[str, Any]]:
        """Extract Person entities from text"""
        persons = []
        # Pattern: Name, age N, works at Company as Position
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+),\s*age\s*(\d+),\s*works\s+at\s+([A-Za-z0-9&\s]+?)\s+as\s+(?:an?\s+)?([A-Za-z\s]+)\.'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            person = {
                "name": match.group(1).strip(),
                "age": int(match.group(2)),
                "position": match.group(4).strip(),
                "department": None  # Will be filled by relation extraction
            }
            persons.append(person)
        
        return persons
    
    def extract_companies(self, text: str) -> List[Dict[str, Any]]:
        """Extract Company entities from text"""
        companies = []
        # Pattern: Company operates/specializes in Industry
        pattern = r'([A-Z][A-Za-z0-9&\s]+?)\s+(?:operates|specializes|focuses|works)\s+in\s+the?\s+([A-Za-z\s,]+?)(?:\.|,)'
        matches = re.finditer(pattern, text)
        
        seen = set()
        for match in matches:
            company_name = match.group(1).strip()
            if company_name not in seen:
                sectors_text = match.group(2).strip()
                sectors = [s.strip() for s in sectors_text.split(' and ')]
                
                company = {
                    "name": company_name,
                    "industry": sectors[0] if sectors else "",
                    "sector": sectors[1] if len(sectors) > 1 else sectors[0],
                    "location": None
                }
                companies.append(company)
                seen.add(company_name)
        
        return companies
    
    def extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract Project entities from text"""
        projects = []
        # Pattern: Project Name started/began on YYYY-MM-DD, ends/concludes on YYYY-MM-DD
        pattern = r'Project\s+([A-Za-z0-9\-]+)\s+(?:started|began|launched|initiated)\s+on\s+(\d{4}-\d{2}-\d{2}),\s+(?:ends|concludes|finishes|completes)\s+on\s+(\d{4}-\d{2}-\d{2})\.'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            # Validate dates
            try:
                start_date = datetime.strptime(match.group(2), '%Y-%m-%d').date()
                end_date = datetime.strptime(match.group(3), '%Y-%m-%d').date()
                
                # Skip invalid dates (e.g., 2023-07-40)
                if end_date <= start_date:
                    continue
                
                project = {
                    "name": match.group(1).strip(),
                    "start_date": match.group(2),
                    "end_date": match.group(3),
                    "status": "Ongoing" if end_date > datetime.now().date() else "Completed",
                    "budget": None
                }
                projects.append(project)
            except ValueError:
                continue
        
        return projects
    
    def extract_departments(self, text: str) -> List[Dict[str, Any]]:
        """Extract Department entities from text"""
        departments = []
        # Infer departments from person positions (e.g., "R&D", "Marketing", "Engineering")
        position_patterns = [
            r'(?:Research|R&D|Engineering|Product|Marketing|Sales|Finance|HR|Operations)',
        ]
        
        found_depts = set()
        for pattern in position_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dept = match.group(0).strip()
                if dept not in found_depts:
                    departments.append({
                        "name": dept,
                        "head": None,
                        "employee_count": None
                    })
                    found_depts.add(dept)
        
        return departments
    
    def extract_positions(self, text: str) -> List[Dict[str, Any]]:
        """Extract Position entities from text"""
        positions = []
        # Extract unique position titles
        pattern = r'works\s+at\s+[A-Za-z0-9&\s]+?\s+as\s+(?:an?\s+)?([A-Za-z\s]+)\.'
        matches = re.finditer(pattern, text)
        
        seen = set()
        for match in matches:
            position_title = match.group(1).strip()
            if position_title not in seen:
                positions.append({
                    "title": position_title,
                    "level": "Mid" if any(x in position_title.lower() for x in ["senior", "lead", "manager"]) else "Entry",
                    "salary_range": None
                })
                seen.add(position_title)
        
        return positions
    
    def extract_technologies(self, text: str) -> List[Dict[str, Any]]:
        """Extract Technology entities from text"""
        technologies = []
        # Look for common technology mentions
        tech_patterns = [
            "Deep Learning Platform",
            "AI",
            "Machine Learning",
            "Cloud",
            "Database",
            "API",
        ]
        
        seen = set()
        for tech in tech_patterns:
            if tech.lower() in text.lower() and tech not in seen:
                technologies.append({
                    "name": tech,
                    "category": "AI" if "AI" in tech or "Learning" in tech else "Infrastructure",
                    "version": None
                })
                seen.add(tech)
        
        return technologies
    
    def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """Extract Location entities from text"""
        locations = []
        # Look for city mentions
        city_pattern = r'(?:Shenzhen|Hangzhou|Beijing|Shanghai|San Francisco|New York|London|Tokyo)'
        matches = re.finditer(city_pattern, text)
        
        seen = set()
        for match in matches:
            city = match.group(0).strip()
            if city not in seen:
                locations.append({
                    "city": city,
                    "country": "China" if city in ["Shenzhen", "Hangzhou", "Beijing", "Shanghai"] else "USA/UK/Japan",
                    "office_type": "Headquarters"
                })
                seen.add(city)
        
        return locations
    
    def extract_teams(self, text: str) -> List[Dict[str, Any]]:
        """Extract Team entities from text"""
        teams = []
        # Look for team mentions
        team_pattern = r'([\w\s]+?\s+Team)'
        matches = re.finditer(team_pattern, text, re.IGNORECASE)
        
        seen = set()
        for match in matches:
            team_name = match.group(1).strip()
            if team_name not in seen:
                teams.append({
                    "name": team_name,
                    "size": None,
                    "focus_area": None
                })
                seen.add(team_name)
        
        return teams
    
    def extract_products(self, text: str) -> List[Dict[str, Any]]:
        """Extract Product entities from text"""
        products = []
        # Look for product mentions
        product_pattern = r'Product[:\s]+([A-Za-z0-9\-\s]+?)(?:v\d+|,|\.|\s+version)'
        matches = re.finditer(product_pattern, text)
        
        seen = set()
        for match in matches:
            product_name = match.group(1).strip()
            if product_name not in seen:
                products.append({
                    "name": product_name,
                    "version": None,
                    "release_date": None
                })
                seen.add(product_name)
        
        return products
    
    def extract_clients(self, text: str) -> List[Dict[str, Any]]:
        """Extract Client entities from text"""
        clients = []
        # Clients are typically companies that hire other companies
        # For now, extract unique company-like entities
        company_pattern = r'\b([A-Z][A-Za-z0-9&\s]+)\b'
        matches = re.finditer(company_pattern, text)
        
        seen = set()
        for match in matches:
            potential_client = match.group(1).strip()
            # Filter to likely client names
            if len(potential_client) > 3 and not potential_client[0].islower() and potential_client not in seen:
                clients.append({
                    "name": potential_client,
                    "contract_value": None,
                    "industry": None
                })
                seen.add(potential_client)
        
        return clients
    
    def extract_all(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all entity types from text"""
        self.extracted_entities = {
            "Person": self.extract_persons(text),
            "Company": self.extract_companies(text),
            "Project": self.extract_projects(text),
            "Department": self.extract_departments(text),
            "Position": self.extract_positions(text),
            "Technology": self.extract_technologies(text),
            "Location": self.extract_locations(text),
            "Team": self.extract_teams(text),
            "Product": self.extract_products(text),
            "Client": self.extract_clients(text),
        }
        return self.extracted_entities
    
    def to_json(self) -> str:
        """Convert extracted entities to JSON format"""
        return json.dumps(self.extracted_entities, indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """Save extracted entities to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_entities, f, indent=2, ensure_ascii=False)
        print(f"Entities saved to {filepath}")


def main():
    """Main function for entity extraction"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python entity_extractor.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "entities_output.json"
    
    # Load entity schema
    schema = {
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
    
    # Read input document
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extract entities
    extractor = EntityExtractor(schema)
    entities = extractor.extract_all(text)
    
    # Save output
    extractor.save_to_file(output_file)
    
    # Print summary
    print("\nEntity Extraction Summary:")
    for entity_type, items in entities.items():
        print(f"{entity_type}: {len(items)} entities found")


if __name__ == "__main__":
    main()
