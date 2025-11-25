import re
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any
from .schema import load_entities_schema, load_relations_schema

ROOT = Path(__file__).resolve().parent


def read_documents(path=None) -> str:
    path = Path(path) if path else ROOT.parent / "documents.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_entities(document_text: str, entities_schema: Dict[str, List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    if entities_schema is None:
        entities_schema = load_entities_schema(ROOT / "data" / "entities.json")

    results = {etype: [] for etype in entities_schema.keys()}

    # Basic person extraction: Name, age, works at Company as Position.
    person_pattern = re.compile(r"(?P<name>[A-Z][a-z]+(?: [A-Z][a-z]+)*), age (?P<age>\d+), works at (?P<company>[^\n,]+) as a (?P<position>[^.]+)")
    for m in person_pattern.finditer(document_text):
        person = {
            "name": m.group("name").strip(),
            "age": int(m.group("age")),
            "position": m.group("position").strip(),
            "department": None
        }
        # Try to map company as department or employer (not exact) - we'll use company name for position department if not found.
        person["department"] = None
        results["Person"].append(person)

    # Company and industry extraction: "X operates in the Y industry" or "X specializes in A and B." or "X focuses on"
    company_pattern = re.compile(r"(?P<name>[A-Z][A-Za-z0-9 &-\.]+?) (?:operates in|specializes in|focuses on|works in|is known for) the (?P<industry>[^\.]*) industry")
    for m in company_pattern.finditer(document_text):
        name = m.group("name").strip()
        industry = m.group("industry").strip()
        entry = {"name": name, "industry": industry, "sector": None, "location": None}
        # Try to extract sector if phrase contains "and"
        if " and " in m.group(0):
            parts = industry.split(" and ")
            if len(parts) > 1:
                entry["sector"] = parts[1].strip()
                entry["industry"] = parts[0].strip()
        results["Company"].append(entry)

    # Special case: company with multiple industries on same line like "Google specializes in Technology and Internet Services." - extract sector
    company_special_pattern = re.compile(r"(?P<name>[A-Z][A-Za-z0-9 &-\.]+?) specializes in (?P<industries>[^\.]+)\.")
    for m in company_special_pattern.finditer(document_text):
        name = m.group("name").strip()
        industries = [p.strip() for p in re.split(r",| and | & ", m.group("industries"))]
        # Find existing company entry and update sector
        found = next((c for c in results["Company"] if c["name"] == name), None)
        if found:
            found["industry"] = industries[0]
            if len(industries) > 1:
                found["sector"] = industries[1]
        else:
            results["Company"].append({"name": name, "industry": industries[0], "sector": industries[1] if len(industries) > 1 else None, "location": None})

    # Project extraction: names, dates
    project_pattern = re.compile(r"Project (?P<name>[A-Za-z0-9\-]+) (?:started|began|launched|initiated) on (?P<start>\d{4}-\d{2}-\d{2}), (?:ends|finishes|completes|concludes) (?:on )?(?P<end>\d{4}-\d{2}-\d{2})")
    for m in project_pattern.finditer(document_text):
        entry = {"name": m.group("name"), "start_date": m.group("start"), "end_date": m.group("end"), "status": None, "budget": None}
        results["Project"].append(entry)

    # Project dates pattern if sentence is slightly different
    project_pattern2 = re.compile(r"Project (?P<name>[A-Za-z0-9\-]+) (?:started on|began on|launched on|initiated on) (?P<start>\d{4}-\d{2}-\d{2}), (?:ends on|finishes on|completes on|concludes on) (?P<end>\d{4}-\d{2}-\d{2})")
    for m in project_pattern2.finditer(document_text):
        entry = {"name": m.group("name"), "start_date": m.group("start"), "end_date": m.group("end"), "status": None, "budget": None}
        if entry not in results["Project"]:
            results["Project"].append(entry)

    # Project lists in "John Doe manages 3 projects: Alpha, Beta, Gamma." and similar
    manager_projects_pattern = re.compile(r"(?P<manager>[A-Z][a-z]+(?: [A-Z][a-z]+)*) manages \d+ projects?: (?P<projects>[^\.\n]+)\.")
    for m in manager_projects_pattern.finditer(document_text):
        manager = m.group("manager").strip()
        projects = [p.strip() for p in re.split(r",\s*| and ", m.group("projects"))]
        # Add manager to persons if not already
        # Connect projects - ensure they exist
        for p in projects:
            if not any(pr["name"] == p for pr in results["Project"]):
                results["Project"].append({"name": p, "start_date": None, "end_date": None, "status": None, "budget": None})

    # Additional person project patterns: "Jane Smith leads 2 projects: Delta, Epsilon." and "Anna Thompson supervises 4 projects: Photon, Electron, Neutron, Proton." etc.
    lead_projects_pattern = re.compile(r"(?P<manager>[A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:leads|oversees|supervises|handles|coordinates|directs) \d+ projects?: (?P<projects>[^\.\n]+)\.")
    for m in lead_projects_pattern.finditer(document_text):
        projects = [p.strip() for p in re.split(r",\s*| and ", m.group("projects"))]
        for p in projects:
            if not any(pr["name"] == p for pr in results["Project"]):
                results["Project"].append({"name": p, "start_date": None, "end_date": None, "status": None, "budget": None})

    # Team extraction from "coordinates 3 projects: Network-A, Network-B, Network-C." or names and such.
    # For this dataset, we'll extract teams mentioned as strings when found in 'coordinates' or 'leads'
    team_pattern = re.compile(r"(?P<name>[A-Z][A-Za-z0-9\-]+(?: [A-Z][A-Za-z0-9\-]+)*) coordinates \d+ projects?: (?P<projects>[^\.\n]+)\.")
    for m in team_pattern.finditer(document_text):
        name = m.group("name").strip()
        results["Team"].append({"name": name, "size": None, "focus_area": None})

    # Department and head extraction. We find phrases like "Department Name" - not available, but we can detect head phrases like "is headed by" or similar.
    dept_head_pattern = re.compile(r"(?P<dept>[A-Z][A-Za-z0-9\-]+) is headed by (?P<person>[A-Z][a-z]+(?: [A-Z][a-z]+)*)\.")
    for m in dept_head_pattern.finditer(document_text):
        results["Department"].append({"name": m.group("dept"), "head": m.group("person"), "employee_count": None})

    # Position types - we can enumerate unique positions found in Person extraction
    positions = set([p["position"] for p in results["Person"] if p.get("position")])
    for pos in positions:
        results["Position"].append({"title": pos, "level": None, "salary_range": None})

    # Recognize Technology, Product, Client where explicit names appear - not always present.
    tech_pattern = re.compile(r"(?P<name>[A-Z][A-Za-z0-9\-]+) (?:specializes|focuses) in (?P<category>[^\.]+)\.")
    # Not perfect, but we can also detect Technology by capitalized words followed by keywords 'platform' or 'technology'
    tech2_pattern = re.compile(r"([A-Z][A-Za-z0-9]+(?: [A-Z][A-Za-z0-9]+)*) (?:Platform|Platform\b|technology|Technology)\b")
    for m in tech2_pattern.finditer(document_text):
        name = m.group(1).strip()
        results["Technology"].append({"name": name, "category": None, "version": None})

    # Product detection pattern - search for 'Product' or product names like 'ShopEngine-v2'
    product_pattern = re.compile(r"[A-Z][a-zA-Z0-9\-]+-v\d")
    for m in product_pattern.finditer(document_text):
        results["Product"].append({"name": m.group(0), "version": None, "release_date": None})

    # Location detection: city, country, office_type - not provided, so leave None

    # Client: names and industries - not present; we'll leave placeholders

    # Clean duplicates
    for etype, lst in results.items():
        unique = []
        seen = set()
        for obj in lst:
            name = obj.get("name") or obj.get("title") or json.dumps(obj, sort_keys=True)
            if name not in seen:
                unique.append(obj)
                seen.add(name)
        results[etype] = unique

    return results


def extract_relations(entities: Dict[str, List[Dict[str, Any]]], document_text: str, relations_schema: Dict[str, Dict[str, str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    if relations_schema is None:
        relations_schema = load_relations_schema(ROOT / "data" / "relations.json")

    rel_results = {r: [] for r in relations_schema.keys()}

    # Build name lookup tables for quick matching
    persons = {p["name"]: p for p in entities.get("Person", []) if p.get("name")}
    companies = {c["name"]: c for c in entities.get("Company", []) if c.get("name")}
    projects = {p["name"]: p for p in entities.get("Project", []) if p.get("name")}
    teams = {t["name"]: t for t in entities.get("Team", []) if t.get("name")}
    products = {pr["name"]: pr for pr in entities.get("Product", []) if pr.get("name")}
    technologies = {t["name"]: t for t in entities.get("Technology", []) if t.get("name")}

    # EmployedBy relations (Person -> Company) from Person 'works at' parsing
    # We need to re-run a more explicit regex for file to match the company in person line
    person_company_pattern = re.compile(r"(?P<name>[A-Z][a-z]+(?: [A-Z][a-z]+)*), age (?P<age>\d+), works at (?P<company>[^,]+) as a (?P<position>[^.]+)")
    for m in person_company_pattern.finditer(document_text):
        name = m.group("name").strip()
        company = m.group("company").strip()
        if name and company:
            rel_results["EmployedBy"].append({"person": name, "company": company})

    # Manages relations from 'manages X projects' or 'leads'/'oversees'
    manage_regex = re.compile(r"(?P<manager>[A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:manages|leads|oversees|supervises|handles|directs) \d+ projects?: (?P<projects>[^\.\n]+)\.")
    for m in manage_regex.finditer(document_text):
        manager = m.group("manager").strip()
        projects_str = m.group("projects")
        projects_names = [p.strip() for p in re.split(r",\s*| and ", projects_str)]
        for p in projects_names:
            rel_results["Manages"].append({"person": manager, "project": p})

    # Company industry relation
    company_ind_pattern = re.compile(r"(?P<name>[A-Z][A-Za-z0-9 &-\.]+?) (?:operates in|specializes in|focuses on|works in|is known for) the (?P<industry>[^\.]*) industry")
    for m in company_ind_pattern.finditer(document_text):
        rel_results["CompanyIndustry"].append({"company": m.group("name").strip(), "industry": m.group("industry").strip()})

    # Project dates and ownership: Find project lines and attach owner based on 'handles/oversees' or 'Company begins on'
    # We can detect 'Project Alpha started on 2023-01-15, ends on 2023-06-30.' and attach dates via ProjectHasDates
    project_date_pattern = re.compile(r"Project (?P<name>[A-Za-z0-9\-]+) (?:started|began|launched|initiated) on (?P<start>\d{4}-\d{2}-\d{2}), (?:ends|finishes|completes|concludes) (?:on )?(?P<end>\d{4}-\d{2}-\d{2})")
    for m in project_date_pattern.finditer(document_text):
        rel_results["ProjectHasDates"].append({"project": m.group("name"), "start_date": m.group("start"), "end_date": m.group("end")})

    # PersonBelongsToDepartment - look for lines where department is mentioned in persons or in other constructs
    # The documents often don't give department data; we'll infer: if they have a position like 'Product Manager', department could be 'Product' or 'Product Management'. We'll do a simple heuristics
    for p in entities.get("Person", []):
        position = p.get("position") or ""
        if position:
            base = position.split()[0]
            department = base if base else None
            if department:
                rel_results["PersonBelongsToDepartment"].append({"person": p["name"], "department": department})

    # DepartmentHead: If pattern 'X manages 3 projects' - infer they lead a team or dept - optional
    # ProjectManages: 'X manages 3 projects: A, B, C.' - we already create 'Manages'

    # TeamUsesTechnology: Not explicit in documents; we'll leave empty unless pattern matches 'AI' or 'Machine Learning' usage
    uses_pattern = re.compile(r"(?P<team>[A-Z][A-Za-z0-9\- ]+) uses (?P<tech>[A-Z][A-Za-z0-9\- ]+)\b")
    for m in uses_pattern.finditer(document_text):
        rel_results["TeamUsesTechnology"].append({"team": m.group("team"), "technology": m.group("tech")})

    # PersonHasPosition
    for p in entities.get("Person", []):
        if p.get("position"):
            rel_results["PersonHasPosition"].append({"person": p["name"], "position": p["position"]})

    # Project owner company: If project started and 'began' with company's context, we can try a heuristic: if company's name precedes project sentences or if company in same paragraph - for now, we leave it blank unless simple matches

    # Clean duplicates
    for r, lst in rel_results.items():
        unique = []
        seen = set()
        for obj in lst:
            key = json.dumps(obj, sort_keys=True)
            if key not in seen:
                unique.append(obj)
                seen.add(key)
        rel_results[r] = unique

    return rel_results


def run_extraction(doc_path=None, entities_path=None, relations_path=None, output_dir=None):
    if output_dir is None:
        output_dir = ROOT.parent / "outputs"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    text = read_documents(doc_path)
    entities_schema = load_entities_schema(entities_path) if entities_path else load_entities_schema()
    relations_schema = load_relations_schema(relations_path) if relations_path else load_relations_schema()

    entities = extract_entities(text, entities_schema)
    relations = extract_relations(entities, text, relations_schema)

    entities_file = output_dir / "entities_output.json"
    relations_file = output_dir / "relations_output.json"
    with open(entities_file, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)
    with open(relations_file, "w", encoding="utf-8") as f:
        json.dump(relations, f, indent=2)

    print(f"Entities written to {entities_file}")
    print(f"Relations written to {relations_file}")
    return entities, relations


if __name__ == "__main__":
    run_extraction()
