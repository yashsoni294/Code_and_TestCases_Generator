from requests.auth import HTTPBasicAuth
from urllib.parse import quote
import requests
from typing import List

def get_project_key(jira_domain: str, email: str, api_token: str, project_name: str) -> str:
    auth = HTTPBasicAuth(email, api_token)
    url = f"https://{jira_domain}/rest/api/2/project"
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch projects: {response.text}")
    
    projects = response.json()
    for project in projects:
        if project.get("name") == project_name:
            return project.get("key")
    raise Exception(f"Project '{project_name}' not found")

def get_description_field_id(jira_domain: str, email: str, api_token: str) -> str:
    auth = HTTPBasicAuth(email, api_token)
    url = f"https://{jira_domain}/rest/api/2/field"
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch fields: {response.text}")
    
    fields = response.json()
    for field in fields:
        if field.get("name") == "Description":
            return field.get("id")
    raise Exception("'Description' field not found")

def fetch_project_stories(jira_domain: str, email: str, api_token: str, project_name: str) -> List[dict]:
    try:
        project_key = get_project_key(jira_domain, email, api_token, project_name)
        description_field_id = get_description_field_id(jira_domain, email, api_token)
    except Exception as e:
        raise e

    auth = HTTPBasicAuth(email, api_token)
    jql_query = f'project = "{project_key}"'
    encoded_jql = quote(jql_query)
    
    start_at = 0
    max_results = 100
    all_issues = []
    
    while True:
        url = (
            f"https://{jira_domain}/rest/api/2/search?"
            f"jql={encoded_jql}&"
            f"fields=summary,{description_field_id}&"
            f"startAt={start_at}&"
            f"maxResults={max_results}"
        )
        
        response = requests.get(url, auth=auth)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch issues: {response.text}")
        
        data = response.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)
        
        if start_at + len(issues) >= data.get("total", 0):
            break
        start_at += len(issues)
    
    stories = []
    for issue in all_issues:
        story = {
            "key": issue.get("key"),
            "summary": issue["fields"].get("summary"),
            "description": issue["fields"].get(description_field_id)
        }
        stories.append(story)
    
    # Sort by issue key numerically
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    return stories
