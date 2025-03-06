from requests.auth import HTTPBasicAuth
import requests
from typing import List, Dict, Any
from urllib.parse import quote
import json
from Logging_folder.logger_file import logger
from pydantic import BaseModel
from fastapi import HTTPException

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

def fetch_specific_stories(jira_domain: str, email: str, api_token: str, project_name: str, sprint_name: str, scrum_list: List[str]):
    try:
        acceptance_criteria_field = get_acceptance_criteria_field_id(jira_domain, email, api_token)
    except Exception as e:
        logger.exception(f"Error fetching acceptance criteria field ID: {e}")
        raise e

    # JQL query to filter by project, sprint, and issue keys
    jql_query = f'project = "{project_name}" AND sprint = "{sprint_name}" AND issuekey in ({", ".join(scrum_list)})'
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

    # Sort stories by issue key numerically
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    return stories

def extract_jira_details(jira_details):
    try:
        jira_details_dict = json.loads(jira_details)
        jira_details_obj = JiraRequest(**jira_details_dict)
        return jira_details_obj
    except json.JSONDecodeError as e:
        logger.exception(f"Invalid JSON for jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON for jira_details: {str(e)}")
    except Exception as e:
        logger.exception(f"Error parsing jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing jira_details: {str(e)}")

def fetch_user_story_acceptance_criteria(jira_details_obj):
    try:
        stories = fetch_specific_stories(
            jira_domain=jira_details_obj.jira_domain,
            email=jira_details_obj.email,
            api_token=jira_details_obj.api_token,
            project_name=jira_details_obj.project_name,
            sprint_name=jira_details_obj.sprint_name,
            scrum_list=jira_details_obj.scrum_list
        )
        user_story_acceptance_criteria = "\n\n".join(
            [f"Story: {story['summary']}\nAcceptance Criteria: {story['acceptance_criteria']}" for story in stories]
        )
        return user_story_acceptance_criteria
    except Exception as e:
        logger.exception(f"Error fetching stories from Jira: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    