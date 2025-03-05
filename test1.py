from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Body
from pydantic import BaseModel, Json
from typing import List, Optional
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote
from fastapi.responses import JSONResponse
from User_story_processing.user_story_logics import excel_sheet_processing
import json

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
    
    stories.sort(key=lambda x: int(x['key'].split('-')[1]))
    return stories

@app.post("/analyze-story/", summary="Analyze user story", response_description="Analysis results of the user story")
async def analyze_user_story(
    user_story_acceptance_criteria: Optional[str] = Form(None),
    excel_file: Optional[UploadFile] = File(None),
    jira_details: Optional[str] = Form(None),  
    framework_test_cases: str = Form(...)
) -> JSONResponse:
    
    # Manually parse JSON from the jira_details string if provided
    jira_details_obj = None
    if jira_details:
        try:
            jira_details_dict = json.loads(jira_details)
            jira_details_obj = JiraRequest(**jira_details_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON for jira_details: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing jira_details: {str(e)}")
    
    # Process Excel file if provided  
    if excel_file:
        user_story_acceptance_criteria = await excel_sheet_processing(excel_file)
        print(user_story_acceptance_criteria)
    
    # Fetch from Jira if details are provided
    elif jira_details_obj:
        print(jira_details_obj)
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
            print(jira_details_obj)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    if not user_story_acceptance_criteria:
        raise HTTPException(status_code=400, detail="No user story data provided. Please provide text, an Excel file, or Jira details.")
    
    # Further processing of user_story_acceptance_criteria as required
    
    return JSONResponse(content={"message": "Analysis completed", "user_story": user_story_acceptance_criteria})