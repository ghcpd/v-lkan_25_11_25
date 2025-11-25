import re
from collections import defaultdict
from typing import Dict, Any, List
from dateutil import parser as dateparser


PERSON_PATTERN = re.compile(
    r"^\s*(?P<name>[^,\n]+), age (?P<age>\d+), works at (?P<company>[^,\n]+) as an? (?P<position>[^.\n]+)\.",
    re.IGNORECASE | re.MULTILINE,
)
PROJECT_OWNERSHIP_PATTERN = re.compile(
    r"^\s*(?P<name>[^,\n]+) (manages|leads|oversees|supervises|handles|coordinates|directs) (?P<count>\d+) projects?: (?P<projects>.+?)\.",
    re.IGNORECASE | re.MULTILINE,
)
PROJECT_DEFINITION_PATTERN = re.compile(
    r"^\s*Project (?P<name>[^ ]+) (started on|began on|launched on|initiated on) (?P<start_date>\d{4}-\d{2}-\d{2}), (ends on|concludes on|finishes on|completes on) (?P<end_date>\d{4}-\d{2}-\d{2})\.",
    re.IGNORECASE | re.MULTILINE,
)
COMPANY_PATTERN = re.compile(
    r"^\s*(?P<company>[^.\n]+?) (operates in|specializes in|focuses on|is known for|works in) (?P<industry>[^.\n]+?)\.",
    re.IGNORECASE | re.MULTILINE,
)


def _safe_date(date_str: str) -> str:
    try:
        # validate date; return ISO string if valid
        dt = dateparser.parse(date_str)
        return dt.date().isoformat()
    except Exception:
        return date_str  # keep raw if invalid


def extract_entities(text: str, schema: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    persons: Dict[str, Dict[str, Any]] = {}
    companies: Dict[str, Dict[str, Any]] = {}
    projects: Dict[str, Dict[str, Any]] = {}

    # Person lines
    for m in PERSON_PATTERN.finditer(text):
        name = m.group("name").strip()
        age = int(m.group("age")) if m.group("age").isdigit() else None
        company = m.group("company").strip()
        position = m.group("position").strip()

        persons.setdefault(name, {k: None for k in schema.get("Person", [])})
        persons[name].update({"name": name, "age": age, "position": position, "department": None})

        companies.setdefault(company, {k: None for k in schema.get("Company", [])})
        companies[company].update({"name": company, "industry": None, "sector": None, "location": None})

    # Project ownership lines by persons
    person_projects_map = defaultdict(list)
    for m in PROJECT_OWNERSHIP_PATTERN.finditer(text):
        name = m.group("name").strip()
        projects_list = [p.strip() for p in m.group("projects").split(",")]
        person_projects_map[name].extend(projects_list)

    # Project definitions
    for m in PROJECT_DEFINITION_PATTERN.finditer(text):
        name = m.group("name").strip()
        start_date = _safe_date(m.group("start_date"))
        end_date = _safe_date(m.group("end_date"))
        projects.setdefault(name, {k: None for k in schema.get("Project", [])})
        projects[name].update(
            {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "status": None,
                "budget": None,
            }
        )

    # Company industries
    for m in COMPANY_PATTERN.finditer(text):
        company = m.group("company").strip()
        industry = m.group("industry").strip()
        companies.setdefault(company, {k: None for k in schema.get("Company", [])})
        companies[company].update({"name": company, "industry": industry})

    # Build result dict respecting schema keys
    results: Dict[str, List[Dict[str, Any]]] = {}
    for entity_type, fields in schema.items():
        if entity_type == "Person":
            results[entity_type] = list(persons.values())
        elif entity_type == "Company":
            results[entity_type] = list(companies.values())
        elif entity_type == "Project":
            results[entity_type] = list(projects.values())
        else:
            results[entity_type] = []
            # fill with empty lists for now (not present in corpus)

    return results, person_projects_map
