from requests.auth import HTTPBasicAuth
import requests
from typing import List
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
    """
    Fetches the field ID for the "Description" field in a Jira instance.

    This function makes an authenticated request to the Jira REST API to retrieve all available fields 
    and extracts the field ID for the "Description" field.

    Args:
        jira_domain (str): The domain of the Jira instance (e.g., "yourcompany.atlassian.net").
        email (str): The email address associated with the Jira account.
        api_token (str): The API token for authentication.

    Returns:
        str: The ID of the "Description" field in Jira.

    Raises:
        Exception: If the request to Jira fails or if the "Description" field is not found.
    """
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
    """
    Fetches specific Jira stories based on a list of issue keys.

    This function retrieves the "summary" and "acceptance criteria" fields for the given issues 
    by making an authenticated request to the Jira REST API. It sorts the stories numerically 
    based on the issue key.

    Args:
        jira_domain (str): The domain of the Jira instance (e.g., "yourcompany.atlassian.net").
        email (str): The email address associated with the Jira account.
        api_token (str): The API token for authentication.
        scrum_list (List[str]): A list of Jira issue keys to fetch.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing:
            - "key" (str): The Jira issue key.
            - "summary" (str): The issue summary.
            - "acceptance_criteria" (str): The acceptance criteria field value.

    Raises:
        Exception: If fetching the acceptance criteria field ID or Jira issues fails.
    """
    try:
        acceptance_criteria_field = get_acceptance_criteria_field_id(jira_domain, email, api_token)
    except Exception as e:
        logger.error(f"Erro is due to the following exception {e}")
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

def extract_jira_details(jira_details):
    """
    Parses a JSON string containing Jira details and converts it into a JiraRequest object.

    This function attempts to deserialize the provided JSON string into a dictionary and 
    instantiate a JiraRequest object with the extracted data.

    Args:
        jira_details (str): A JSON-formatted string containing Jira details.

    Returns:
        JiraRequest: An instance of JiraRequest initialized with the extracted details.

    Raises:
        HTTPException (400): If the JSON is invalid or if an error occurs while parsing.
    """
    try:
        jira_details_dict = json.loads(jira_details)
        jira_details_obj = JiraRequest(**jira_details_dict)
        return jira_details_obj
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON for jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON for jira_details: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing jira_details: {str(e)}")
        
def fetch_user_story_acceptance_criteria(jira_details_obj):
    """
    Fetches user stories and their acceptance criteria from Jira.

    This function retrieves specific user stories based on the provided Jira details, 
    formats them, and returns a string containing the story summaries along with their 
    acceptance criteria.

    Args:
        jira_details_obj (JiraRequest): An object containing Jira domain, authentication 
        details, and a list of issue keys.

    Returns:
        str: A formatted string listing user stories and their acceptance criteria.

    Raises:
        HTTPException (500): If an error occurs while fetching stories from Jira.
    """
    try:
        stories = fetch_specific_stories(
            jira_domain=jira_details_obj.jira_domain,
            email=jira_details_obj.email,
            api_token=jira_details_obj.api_token,
            scrum_list=jira_details_obj.scrum_list
        )
        user_story_acceptance_criteria = "\n\n".join(
            [f"Story: {story['summary']}\nAcceptance Criteria: {story['acceptance_criteria']}" for story in stories]
        )
        return user_story_acceptance_criteria
    except Exception as e:
        logger.error(f"Error fetching stories from Jira: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))