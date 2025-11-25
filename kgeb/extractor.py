import re
import json
from datetime import datetime
from typing import Dict, List, Any


class EntityExtractor:
    def __init__(self, schema_path: str):
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def parse_person_line(self, line: str) -> Dict[str, Any]:
        # Example: John Doe, age 32, works at OpenAI as a Researcher.
        m = re.match(r"\s*([A-Za-z \-']+), age (\d+), works at ([A-Za-z0-9 &\-]+) as an? (.+?)\.?$", line)
        if not m:
            return {}
        name, age, company, position = m.groups()
        return {"name": name.strip(), "age": int(age), "position": position.strip(), "department": None}

    def parse_company_line(self, line: str) -> Dict[str, Any]:
        # Example: OpenAI operates in the Technology industry.
        m = re.match(r"\s*([A-Za-z0-9 &\-]+) (operates in|specializes in|focuses on|is known for) (.+?)\.?$", line)
        if not m:
            return {}
        name, _, rest = m.groups()
        industry = rest.strip()
        # attempt to split industry and sector
        sector = None
        location = None
        return {"name": name.strip(), "industry": industry, "sector": sector, "location": location}

    def parse_person_projects(self, line: str) -> List[Dict[str, Any]]:
        # Example: John Doe manages 3 projects: Alpha, Beta, Gamma.
        m = re.match(r"\s*([A-Za-z \-']+) (manages|leads|oversees|supervises|handles|coordinates|directs) (?:\d+ )?projects?: (.+?)\.?$", line)
        if not m:
            return []
        name, _, projects = m.groups()
        projects = [p.strip() for p in projects.split(",")]
        return [{"person": name.strip(), "project": p} for p in projects if p]

    def parse_project_line(self, line: str) -> Dict[str, Any]:
        # Example: Project Alpha started on 2023-01-15, ends on 2023-06-30.
        m = re.match(r"\s*Project\s+(.+?) (started on|began on|began|launched on|initiated on|initiated) (\d{4}-\d{2}-\d{2}), (?:ends on|finishes on|completes on|concludes on|finishes) (\d{4}-\d{2}-\d{2})\.?$", line)
        if not m:
            # try variants like: Project Alpha started on 2023-01-15, ends on 2023-06-30.
            m2 = re.match(r"\s*Project\s+(.+?) (started on|began on|began|launched on|initiated on|initiated) (\d{4}-\d{2}-\d{2}), (?:ends on|finishes on|completes on|concludes on|finishes) (\d{4}-\d{2}-\d{2})\.?$", line)
            if not m2:
                return {}
            name, _, start, end = m2.groups()
        else:
            name, _, start, end = m.groups()

        sd = None
        ed = None
        try:
            sd = datetime.fromisoformat(start).date()
        except Exception:
            sd = None
        try:
            ed = datetime.fromisoformat(end).date()
        except Exception:
            ed = None

        # Determine status safely
        if ed is not None:
            status = "ongoing" if ed >= datetime.now().date() else "completed"
        elif sd is not None:
            # has start date but no valid end: if start is in future mark scheduled, otherwise ongoing
            status = "scheduled" if sd > datetime.now().date() else "ongoing"
        else:
            status = "unknown"

        return {"name": name.strip(), "start_date": str(start), "end_date": str(end), "status": status, "budget": None}

    def extract_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        entities = {k: [] for k in self.schema.keys()}
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        for line in lines:
            # Persons
            p = self.parse_person_line(line)
            if p:
                entities["Person"].append(p)
                continue

            # Companies
            c = self.parse_company_line(line)
            if c:
                entities["Company"].append(c)
                continue

            # Person -> project relationships (will be picked up in relation extractor but capture as minimal entity refs)
            pp = self.parse_person_projects(line)
            if pp:
                for rel in pp:
                    # ensure project entity placeholder
                    entities.setdefault("Project", [])
                    for rh in pp:
                        entities["Project"].append({"name": rh["project"], "start_date": None, "end_date": None, "status": None, "budget": None})
                continue

            # Projects
            pr = self.parse_project_line(line)
            if pr:
                entities["Project"].append(pr)
                continue

            # Generic fallback: try to find simple key:value style
        # De-duplicate entities naive by name when available
        for etype, items in list(entities.items()):
            seen = set()
            deduped = []
            for it in items:
                key = tuple(sorted([(k, str(v)) for k, v in it.items()])) if it else None
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(it)
            entities[etype] = deduped

        return entities

    def extract_from_file(self, path: str) -> Dict[str, List[Dict[str, Any]]]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return self.extract_from_text(text)
