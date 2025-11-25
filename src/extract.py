import re
import json
from datetime import datetime

ENTITIES = json.load(open('entities.json'))

def parse_documents(path='documents.txt'):
    people = []
    companies = []
    projects = []
    relations = {'BelongsTo': [], 'Manages': [], 'CompanyIndustry': []}

    with open(path, encoding='utf-8') as f:
        text = f.read()

    # Person lines: "Name, age X, works at COMPANY as a POSITION."
    person_pattern = re.compile(r"([A-Z][a-z]+(?: [A-Z][a-z]+)*), age (\d+), works at ([A-Za-z0-9& ]+) as an? ([A-Za-z0-9\- ]+)")
    for m in person_pattern.finditer(text):
        name, age, company, position = m.groups()
        person = {'name': name, 'age': int(age), 'position': position.strip(), 'department': None}
        people.append(person)
        relations['BelongsTo'].append({'person': name, 'company': company.strip()})

    # Company lines with industry
    company_pattern = re.compile(r"([A-Z][A-Za-z0-9& ]+?) operates in the ([A-Za-z &]+) industry")
    for m in company_pattern.finditer(text):
        name, industry = m.groups()
        company = {'name': name.strip(), 'industry': industry.strip(), 'sector': None, 'location': None}
        companies.append(company)
        relations['CompanyIndustry'].append({'company': name.strip(), 'industry': industry.strip()})

    # Project lines: "Project Alpha started on 2023-01-15, ends on 2023-06-30."
    proj_pattern = re.compile(r"Project ([A-Za-z0-9\-]+) (?:started|began|launched|initiated) on (\d{4}-\d{2}-\d{2}), (?:ends on|ends|concludes on|finishes on|completes on) (\d{4}-\d{2}-\d{2})")
    for m in proj_pattern.finditer(text):
        name, start, end = m.groups()
        start_d = start
        end_d = end
        status = 'Completed' if datetime.strptime(end_d, '%Y-%m-%d') < datetime.now() else 'Ongoing'
        project = {'name': name, 'start_date': start_d, 'end_date': end_d, 'status': status, 'budget': None}
        projects.append(project)

    # Relations: person manages/handles/oversees projects
    manager_pattern = re.compile(r"([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:manages|leads|oversees|supervises|handles|coordinates|directs) (?:\d+ projects: )?([A-Za-z0-9, \-]+)\.")
    for m in manager_pattern.finditer(text):
        manager, proj_list = m.groups()
        proj_names = [p.strip() for p in proj_list.split(',')]
        for p in proj_names:
            if p:
                relations['Manages'].append({'person': manager, 'project': p})

    out_entities = {'Person': people, 'Company': companies, 'Project': projects}
    return out_entities, relations

def save_outputs(entities, relations, out_ent='entities_output.json', out_rel='relations_output.json'):
    with open(out_ent, 'w', encoding='utf-8') as f:
        json.dump(entities, f, indent=2)
    with open(out_rel, 'w', encoding='utf-8') as f:
        json.dump(relations, f, indent=2)

if __name__ == '__main__':
    entities, relations = parse_documents('documents.txt')
    save_outputs(entities, relations)
    print('Extraction complete. Wrote entities_output.json and relations_output.json')
