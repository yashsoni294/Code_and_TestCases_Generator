from requests.auth import HTTPBasicAuth
import requests
from typing import List
from urllib.parse import quote

def get_acceptance_criteria_field_id(jira_domain: str, email: str, api_token: str):
    auth = HTTPBasicAuth(email, api_token)
    url = f"https://{jira_domain}/rest/api/2/field"
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch fields: {response.text}")
    
    fields = response.json()
    for field in fields:
        if field.get("name") == "Description":
            return field.get("id")
    raise Exception("'Description' field not found!")


def fetch_specific_stories(jira_domain: str, email: str, api_token: str, project_name: str, sprint_name: str, scrum_list: List[str]):
    try:
        acceptance_criteria_field = get_acceptance_criteria_field_id(jira_domain, email, api_token)
    except Exception as e:
        raise e
    
    jql_query = (
        f'project = "{project_name}" AND sprint = "{sprint_name}" AND issuekey in ({", ".join(scrum_list)})'
    )
    encoded_jql = quote(jql_query)
    
    auth = HTTPBasicAuth(email, api_token)
    url = (
        f"https://{jira_domain}/rest/api/2/search?"
        f"jql={encoded_jql}&"
        f"fields=summary,{acceptance_criteria_field}&"
        "maxResults=100"
    )
    
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch issues: {response.text}")
    
    data = response.json()
    stories = []
    for issue in data.get("issues", []):
        story = {
            "key": issue.get("key"),
            "summary": issue["fields"].get("summary"),
            "acceptance_criteria": issue["fields"].get(acceptance_criteria_field)
        }
        stories.append(story)
    
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    return stories