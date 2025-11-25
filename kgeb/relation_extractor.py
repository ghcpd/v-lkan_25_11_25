import json
import re
from typing import Dict, List, Any


class RelationExtractor:
    def __init__(self, relations_schema_path: str):
        with open(relations_schema_path, "r", encoding="utf-8") as f:
            self.relations_def = json.load(f)

    def extract_relations_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        relations = {r["name"]: [] for r in self.relations_def}

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        for line in lines:
            # works at -> EmployeeOf / WorksAt
            m = re.match(r"([A-Za-z \-']+), age \d+, works at ([A-Za-z0-9 &\-]+) as an? (.+?)\.?$", line)
            if m:
                person, company, position = m.groups()
                relations.setdefault("WorksAt", []).append({"person": person.strip(), "company": company.strip()})
                continue

            # person manages projects
            m2 = re.match(r"([A-Za-z \-']+) (manages|leads|oversees|supervises|handles|coordinates|directs) (?:\d+ )?projects?: (.+?)\.?$", line)
            if m2:
                person = m2.group(1)
                projects = [p.strip() for p in m2.group(3).split(",")]
                for proj in projects:
                    relations.setdefault("ManagesProject", []).append({"person": person.strip(), "project": proj})
                continue

            # company industry relationships
            m3 = re.match(r"([A-Za-z0-9 &\-]+) (operates in|specializes in|focuses on|is known for) (.+?)\.?$", line)
            if m3:
                company = m3.group(1).strip()
                industry = m3.group(3).strip()
                relations.setdefault("CompanyIndustry", []).append({"company": company, "industry": industry})
                continue

            # project start / end mention may not imply owner but we can find dates
        return relations

    def extract_from_file(self, path: str) -> Dict[str, List[Dict[str, Any]]]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return self.extract_relations_from_text(text)
