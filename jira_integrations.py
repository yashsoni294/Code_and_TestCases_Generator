from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import List
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

app = FastAPI()

class JiraRequest(BaseModel):
    jira_domain: str
    email: str
    api_token: str
    project_name: str
    sprint_name: str
    scrum_list: List[str]

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

def fetch_specific_stories(jira_domain: str, email: str, api_token: str, scrum_list: List[str]):
    try:
        acceptance_criteria_field = get_acceptance_criteria_field_id(jira_domain, email, api_token)
    except Exception as e:
        raise e
    
    # Build JQL query for specified issue keys
    jql_query = f'issuekey in ({", ".join(scrum_list)})'
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
    
    # Sort stories by their issue key numerically
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    return stories

@app.post("/get-stories")
def get_stories(request: JiraRequest):
    try:
        stories = fetch_specific_stories(
            jira_domain=request.jira_domain,
            email=request.email,
            api_token=request.api_token,
            scrum_list=request.scrum_list
        )
        return {"stories": stories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
