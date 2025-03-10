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

def get_acceptance_criteria_field_id(jira_domain: str, email: str, api_token: str) -> str:
    """
    Fetches the field ID for the 'Description' field from a Jira instance.
    
    Args:
        jira_domain (str): The domain of the Jira instance (e.g., 'yourcompany.atlassian.net').
        email (str): The email address associated with the Jira account.
        api_token (str): The API token for authentication.
    
    Returns:
        str: The field ID corresponding to the 'Description' field.
    
    Raises:
        Exception: If the request fails or if the 'Description' field is not found.
    """
    # Authenticate using basic authentication with the provided email and API token
    auth = HTTPBasicAuth(email, api_token)
    
    # Construct the API endpoint URL for fetching Jira fields
    url = f"https://{jira_domain}/rest/api/2/field"
    
    # Make a GET request to the Jira API to retrieve field data
    response = requests.get(url, auth=auth)
    
    # Check if the request was successful (HTTP status code 200)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch fields: {response.text}")
    
    # Parse the JSON response containing all available fields
    fields = response.json()
    
    # Iterate through the fields to find the one named 'Description'
    for field in fields:
        if field.get("name") == "Description":
            return field.get("id")  # Return the field ID if found
    
    # Raise an exception if the 'Description' field is not found
    raise Exception("'Description' field not found!")

def fetch_specific_stories(jira_domain: str, email: str, api_token: str, project_name: str, sprint_name: str, scrum_list: List[str]):
    """
    Fetches specific Jira stories based on a given project, sprint, and a list of issue keys.

    Args:
        jira_domain (str): The Jira domain (e.g., "yourcompany.atlassian.net").
        email (str): The email associated with the Jira account.
        api_token (str): The API token for authentication.
        project_name (str): The Jira project name.
        sprint_name (str): The sprint name to filter issues.
        scrum_list (List[str]): List of issue keys to fetch.

    Returns:
        List[dict]: A list of dictionaries containing story details (key, summary, acceptance criteria).

    Raises:
        Exception: If an error occurs while fetching stories.
    """
    try:
        # Retrieve the custom field ID for acceptance criteria
        acceptance_criteria_field = get_acceptance_criteria_field_id(jira_domain, email, api_token)
    except Exception as e:
        logger.exception(f"Error fetching acceptance criteria field ID: {e}")
        raise e

    # Construct JQL query to filter issues by project, sprint, and issue keys
    jql_query = f'project = "{project_name}" AND sprint = "{sprint_name}" AND issuekey in ({", ".join(scrum_list)})'
    encoded_jql = quote(jql_query)  # URL encode the JQL query
    
    # Set up authentication
    auth = HTTPBasicAuth(email, api_token)
    
    # Construct the API request URL
    url = (
        f"https://{jira_domain}/rest/api/2/search?"
        f"jql={encoded_jql}&"
        f"fields=summary,{acceptance_criteria_field}&"
        "maxResults=100"
    )

    # Send the request to fetch issues
    response = requests.get(url, auth=auth)
    
    # Check if the response is successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch issues: {response.text}")
    
    # Parse the response JSON
    data = response.json()
    stories = []
    
    # Extract relevant issue details
    for issue in data.get("issues", []):
        story = {
            "key": issue.get("key"),  # Jira issue key (e.g., "PROJ-123")
            "summary": issue["fields"].get("summary"),  # Issue summary/title
            "acceptance_criteria": issue["fields"].get(acceptance_criteria_field)  # Acceptance criteria field
        }
        stories.append(story)

    # Sort stories numerically based on the issue key (assumes format "PROJECT-123")
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    
    return stories

def extract_jira_details(jira_details):
    """
    Parses a JSON string containing Jira details and converts it into a JiraRequest object.

    Args:
        jira_details (str): A JSON-formatted string representing Jira issue details.

    Returns:
        JiraRequest: An instance of JiraRequest populated with the parsed JSON data.

    Raises:
        HTTPException: If the input JSON is invalid or if any other error occurs during parsing.
    """
    try:
        # Parse the JSON string into a dictionary
        jira_details_dict = json.loads(jira_details)

        # Convert the dictionary into a JiraRequest object
        jira_details_obj = JiraRequest(**jira_details_dict)

        return jira_details_obj

    except json.JSONDecodeError as e:
        # Log and raise an exception if the input is not a valid JSON
        logger.exception(f"Invalid JSON for jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON for jira_details: {str(e)}")

    except Exception as e:
        # Log and raise an exception for any other unexpected errors
        logger.exception(f"Error parsing jira_details: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing jira_details: {str(e)}")
    
def fetch_user_story_acceptance_criteria(jira_details_obj):
    """
    Fetches user stories and their acceptance criteria from Jira based on the provided details.

    Parameters:
        jira_details_obj (object): An object containing Jira connection details, including:
            - jira_domain (str): The Jira domain URL.
            - email (str): User email for authentication.
            - api_token (str): API token for authentication.
            - project_name (str): Name of the Jira project.
            - sprint_name (str): Name of the sprint to fetch stories from.
            - scrum_list (list): List of scrum team members (if applicable).

    Returns:
        str: A formatted string containing user stories and their respective acceptance criteria.

    Raises:
        HTTPException: If there is an error fetching stories from Jira, returns a 500 status code.
    """
    try:
        # Fetch specific user stories from Jira based on the provided details
        stories = fetch_specific_stories(
            jira_domain=jira_details_obj.jira_domain,
            email=jira_details_obj.email,
            api_token=jira_details_obj.api_token,
            project_name=jira_details_obj.project_name,
            sprint_name=jira_details_obj.sprint_name,
            scrum_list=jira_details_obj.scrum_list
        )
        
        # Format the fetched stories and their acceptance criteria into a readable string
        user_story_acceptance_criteria = "\n\n".join(
            [f"Story: {story['summary']}\nAcceptance Criteria: {story['acceptance_criteria']}" for story in stories]
        )
        
        return user_story_acceptance_criteria
    
    except Exception as e:
        # Log the error and raise an HTTPException with a 500 status code
        logger.exception(f"Error fetching stories from Jira: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))