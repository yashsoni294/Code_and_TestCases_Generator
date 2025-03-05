# import requests
# from requests.auth import HTTPBasicAuth
# import json
# from urllib.parse import quote

# # Replace these with your details
# JIRA_DOMAIN = "samta-team.atlassian.net"  # e.g., "mycompany.atlassian.net"
# EMAIL = "hrishabh.dubey@samta.ai"
# API_TOKEN = "ATATT3xFfGF0dgAwIepKIuosoTuX23AlGhP23bTE3Ze9qawbpKeIT9OcGs79IzJwDUHyq-aAQj4OtHh1waPPA-L0iEvGpI-NgC-mEbHwpKauLdiLiQEMGtTc94ixepSUq89WOj6Pi5diAzHbQ5zJrsp0SRWyG4jJHqSGy_DHGZwkzSaeoz4FVe4=1189F397"
# PROJECT_NAME = "My Scrum Project"
# SPRINT_NAME = "Sprint 1"
# ISSUE_KEYS = ["SCRUM-23", "SCRUM-24", "SCRUM-25", "SCRUM-26"]  # Focus on these keys

# auth = HTTPBasicAuth(EMAIL, API_TOKEN)

# def get_acceptance_criteria_field_id():
#     url = f"https://{JIRA_DOMAIN}/rest/api/2/field"
#     response = requests.get(url, auth=auth)
    
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch fields: {response.text}")
    
#     fields = response.json()
#     for field in fields:
#         if field.get("name") == "Description":
#             return field.get("id")
#     raise Exception("'Description' field not found!")

# def fetch_specific_stories():
#     acceptance_criteria_field = get_acceptance_criteria_field_id()
    
#     # Build JQL query strictly for the selected issue keys
#     jql_query = f'issuekey in ({", ".join(ISSUE_KEYS)})'
#     encoded_jql = quote(jql_query)
    
#     url = (
#         f"https://{JIRA_DOMAIN}/rest/api/2/search?"
#         f"jql={encoded_jql}&"
#         f"fields=summary,{acceptance_criteria_field}&"
#         "maxResults=100"
#     )
    
#     response = requests.get(url, auth=auth)
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch issues: {response.text}")
    
#     data = response.json()
#     stories = []
#     for issue in data.get("issues", []):
#         story = {
#             "key": issue.get("key"),
#             "summary": issue["fields"].get("summary"),
#             "acceptance_criteria": issue["fields"].get(acceptance_criteria_field)
#         }
#         stories.append(story)
    
#     # Sort stories by their issue key in ascending order
#     stories.sort(key=lambda x: int(x['key'].split('-')[1]))
#     return stories

# if __name__ == "__main__":
#     try:
#         specific_stories = fetch_specific_stories()
#         print("Stories from SCRUM-23 to SCRUM-26:")
#         for story in specific_stories:
#             print(f"\nStory: {story['key']} - {story['summary']}")
#             print(f"Acceptance Criteria:\n{story['acceptance_criteria']}")
#             print("-" * 50)
#     except Exception as e:
#         print(f"Error: {str(e)}")



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
    
