import re
from typing import Dict, Any, List
from .entity_extractor import PERSON_PATTERN, COMPANY_PATTERN, PROJECT_DEFINITION_PATTERN


REL_WORKS_AT = "WorksAt"
REL_MANAGES_PROJECT = "ManagesProject"
REL_COMPANY_INDUSTRY = "CompanyOperatesInIndustry"
REL_PROJECT_DATES = "ProjectHasDates"


def extract_relations(
    text: str,
    relations_schema: Dict[str, Dict[str, Any]],
    person_projects_map: Dict[str, List[str]] | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    relations: Dict[str, List[Dict[str, Any]]] = {rel: [] for rel in relations_schema.keys()}

    # WorksAt relations from person lines
    for m in PERSON_PATTERN.finditer(text):
        name = m.group("name").strip()
        company = m.group("company").strip()
        if REL_WORKS_AT in relations:
            relations[REL_WORKS_AT].append({"person": name, "company": company})

    # Person -> Project management relations
    if person_projects_map:
        for person, projects in person_projects_map.items():
            for project in projects:
                if REL_MANAGES_PROJECT in relations:
                    relations[REL_MANAGES_PROJECT].append({"person": person, "project": project})

    # Company -> Industry relations
    for m in COMPANY_PATTERN.finditer(text):
        company = m.group("company").strip()
        industry = m.group("industry").strip()
        if REL_COMPANY_INDUSTRY in relations:
            relations[REL_COMPANY_INDUSTRY].append({"company": company, "industry": industry})

    # Project dates
    for m in PROJECT_DEFINITION_PATTERN.finditer(text):
        project = m.group("name").strip()
        start_date = m.group("start_date").strip()
        end_date = m.group("end_date").strip()
        if REL_PROJECT_DATES in relations:
            relations[REL_PROJECT_DATES].append({"project": project, "start_date": start_date, "end_date": end_date})

    # Return relations dict (empty lists for others)
    return relations
