from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from typing import Optional
from fastapi.responses import JSONResponse
from User_story_processing.user_story_logics import excel_sheet_processing
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import openai
from dotenv import load_dotenv
from Templates import prompt_templates
import base64
from Logging_folder.logger_file import logger
from Model_calling.openai_calling import get_conversation_openai
from Utils_folder import utils
from File_Insertion.insertion_script import write_markdown_file, write_word_file, write_text_file, improve_code_snippet, code_insertion, create_unique_folder, get_folder_details
from User_story_processing.jira_integration import extract_jira_details, fetch_user_story_acceptance_criteria

app = FastAPI()

# Load API Key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY
    
# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods for development
    allow_headers=["*"], # Allows all headers for development
)

@app.post("/analyze-story/", summary="Analyze user story", response_description="Analysis results of the user story")
async def analyze_user_story(
    user_story_acceptance_criteria: Optional[str] = Form(None),
    excel_file: Optional[UploadFile] = File(None),
    jira_details: Optional[str] = Form(None),
    framework_test_cases: str = Form(...)) -> JSONResponse:
    """
    Analyze a user story and generate relevant artifacts based on the selected framework.

    This endpoint processes a user story and its acceptance criteria from various sources 
    (user input, Excel file, or Jira). It then generates relevant outputs based on the selected 
    framework, such as API contracts, test cases, or code files.

    Args:
        user_story_acceptance_criteria (Optional[str]): The acceptance criteria of the user story.
        excel_file (Optional[UploadFile]): An Excel file containing the user story details.
        jira_details (Optional[str]): Jira details to fetch the user story acceptance criteria.
        framework_test_cases (str): The target framework or test case generation option. 
            - "ReactJs_Typescript": Generates ReactJS + TypeScript frontend code.
            - "Test_cases_Generation": Generates test cases.
            - "FastAPI": Generates FastAPI-based backend code.
            - "Django": Generates Django-based backend code.

    Returns:
        JSONResponse: A JSON object containing:
            - message (str): Success message indicating the generated output.
            - folder_path (str): The path where generated files are stored.
            - zip_path (str): Path to the ZIP file containing the generated files.

    Raises:
        HTTPException: Returns a 500 error if an exception occurs during processing.

    Processing Steps:
    1. Extracts the user story acceptance criteria from the given source.
    2. If "ReactJs_Typescript" is selected:
        - Generates API contracts, writes them to Markdown/Word files.
        - Generates ReactJS code, improves it, and structures it in folders.
    3. If "Test_cases_Generation" is selected:
        - Generates test cases from the user story and writes them to Excel/Markdown.
    4. If "FastAPI" or "Django" is selected:
        - Generates backend code with API contracts and structures the output.
    5. Creates a ZIP archive of the generated files and returns its path.

    """
    # Create a unique id for creteing unique folder name.
    unique_id = uuid.uuid4().hex

    jira_details_obj = None
    if jira_details:
        jira_details_obj = extract_jira_details(jira_details)
    
    # Process Excel file if provided  
    if excel_file:
        user_story_acceptance_criteria = await excel_sheet_processing(excel_file)
        logger.info(f"Fetched user story acceptance criteria from Excel sheet: {user_story_acceptance_criteria}")
    
    # Fetch from Jira if details are provided
    elif jira_details_obj:
        user_story_acceptance_criteria = fetch_user_story_acceptance_criteria(jira_details_obj)
        logger.info(f"Fetched user story acceptance criteria from Jira: {user_story_acceptance_criteria}")
    try:
        if framework_test_cases == "ReactJs_Typescript":
            base_path = os.getenv("FRONTEND_BASE_FOLDER") + "/Code_folder"
            
            # Create a unique folder inside the provided base path
            base_path = create_unique_folder(base_path, unique_id)

            user_story_filter_template = prompt_templates.user_story_filter_template.format(user_story_accpt_criet = user_story_acceptance_criteria)
            logger.info("Processing the User story and acceptance criteria to make it detailed and arranged ...")

            user_story_accpt_criet = get_conversation_openai(template = user_story_filter_template)
            logger.info("Successfully processed the User story and acceptance criteria.")

            logger.info("Generating the API contract for the User story and acceptance criteria ...")
            api_contract_gen_template = prompt_templates.api_contract_gen_template.format(user_story_accpt_criet = user_story_accpt_criet)
            
            api_contract = utils.replace_braces(get_conversation_openai(template = api_contract_gen_template))
            logger.info("Successfully generated the API contract for the User story and acceptance criteria.")

            logger.info("Writting the API contract in Markdown(.md) file ...")
            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.md"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_markdown_file(full_path, api_contract)

            logger.info("Writting the API contract in Word(.docx) file ...")
            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.docx"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_word_file(full_path, api_contract)

            reactJS_code_gen_template = prompt_templates.reactJS_code_gen_template.format(user_story_accpt_criet = user_story_accpt_criet, api_contract = api_contract)
           
            logger.info("Generating Code for the User story and acceptance criteria according to the API contract ...")
            gen_code = get_conversation_openai(template = reactJS_code_gen_template)
            logger.info("Successfully generated Code for the User story and acceptance criteria according to the API contract.")   

            # Specify the file name and path
            file_name = "Gen_code.txt"  # Writing to the root folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_text_file(full_path, gen_code)

            logger.info("Improving the Code Quality of the Generated Code making it well commented also adding Documentation ...")
            
            improved_gen_code = improve_code_snippet(gen_code, base_path)
        
            code_insertion(improved_gen_code, base_path)
            
            # output_zip = r"/mnt/c/Users/Asus/Desktop/Code Files/Code_Gen_BackEnd/FrontEnd_Generation/Zip_folder/"
            output_zip = os.getenv("FRONTEND_BASE_FOLDER") + "/Zip_folder"
            
            # Creates a 32-character hexadecimal string & Update base_path to point to the new unique folder
            output_zip = os.path.join(output_zip, f"{unique_id}.zip")

            utils.create_zip_of_folder(base_path, output_zip)

            return {
                "message": "ReactJS Code is successfully Generated with Files and Folder Structure.",
                "folder_path": base_path,
                "zip_path": output_zip
                
            }
        
        elif framework_test_cases == "Test_cases_Generation":
            base_path = os.getenv("TEST_CASES_BASE_FOLDER") + "/TestCases_folder"

            base_path = create_unique_folder(base_path, unique_id)

            user_story_filter_template = prompt_templates.user_story_filter_template.format(user_story_accpt_criet = user_story_acceptance_criteria)
            
            logger.info("Processing the User story and acceptance criteria to make it detailed and arranged ...")
            user_story_accpt_criet = get_conversation_openai(template = user_story_filter_template)
            logger.info("Successfully processed the User story and acceptance criteria.")

            test_cases_gen_template = prompt_templates.test_cases_gen_template.format(user_story_accpt_criet = user_story_accpt_criet)
 
            logger.info("Generating the Test Cases for the User story and acceptance criteria ...")
            test_cases = get_conversation_openai(template = test_cases_gen_template)

            logger.info("Successfully generated the Test Cases for the User story and acceptance criteria.")
            # Extract test cases from markdown
            test_cases_excell = utils.extract_test_cases(test_cases)
            logger.info("Writing the test cases in Excell (.xlsx) file ...")

            # Specify the file name
            file_name = "Gen_test_cases.xlsx"  # Ensure you have permissions to write to the root folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            # Write test cases to Excel
            utils.write_to_excel(test_cases_excell, full_path)

            logger.info("Writing test cases to Markdown(.md) file ...")
            # Specify the file name for the Markdown file
            file_name = "Gen_Test_cases.md"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_markdown_file(full_path, test_cases)

            output_zip = os.getenv("TEST_CASES_BASE_FOLDER") + "/Zip_folder/"
            
            # Creates a 32-character hexadecimal string & Update base_path to point to the new unique folder
            output_zip = os.path.join(output_zip, f"{unique_id}.zip")

            utils.create_zip_of_folder(base_path, output_zip)

            return {
                "message": "Test Cases are successfully Generated and Created Files and Folder Structure.",
                "folder_path": base_path,
                "zip_path": output_zip
                
            }
        
        elif framework_test_cases == "FastAPI":
            base_path = os.getenv("BACKEND_BASE_FOLDER") + "/Code_folder"
            
            base_path = create_unique_folder(base_path, unique_id)

            user_story_filter_template = prompt_templates.user_story_filter_template.format(user_story_accpt_criet = user_story_acceptance_criteria)
      
            logger.info("Processing the User story and acceptance criteria to make it detailed and arranged ...")
            user_story_accpt_criet = get_conversation_openai(template = user_story_filter_template)
            logger.info("Successfully processed the User story and acceptance criteria.")

            logger.info("Generating the API contract for the User story and acceptance criteria ...")
            api_contract_gen_template = prompt_templates.api_contract_gen_template.format(user_story_accpt_criet = user_story_accpt_criet)

            api_contract = utils.replace_braces(get_conversation_openai(template = api_contract_gen_template))
            logger.info("Successfully generated the API contract for the User story and acceptance criteria.")
            
            logger.info("Writting the API contract in Markdown(.md) file ...")
            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.md"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_markdown_file(full_path, api_contract)

            logger.info("Writting the API contract in Word(.docx) file ...")
            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.docx"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_word_file(full_path, api_contract)

            fastapi_code_gen_template = prompt_templates.fastapi_code_gen_template.format(user_story_accpt_criet = user_story_accpt_criet, api_contract = api_contract)
        
            logger.info("Generating Code for the User story and acceptance criteria according to the API contract ...")
            gen_code = get_conversation_openai(template = fastapi_code_gen_template)

            logger.info("Successfully generated Code for the User story and acceptance criteria according to the API contract.")   
            # Specify the file name and path
            file_name = "Gen_code.txt"  # Writing to the root folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_text_file(full_path, gen_code)

            logger.info("Improving the Code Quality of the Generated Code making it well commented also adding Documentation ...")
            
            improved_gen_code = improve_code_snippet(gen_code, base_path)
            
            code_insertion(improved_gen_code, base_path)

            # output_zip = r"/mnt/c/Users/Asus/Desktop/Code Files/Code_Gen_BackEnd/BackEnd_Generation/Zip_folder/"
            output_zip = os.getenv("BACKEND_BASE_FOLDER") + "/Zip_folder/"
            
            # Creates a 32-character hexadecimal string & Update base_path to point to the new unique folder
            output_zip = os.path.join(output_zip, f"{unique_id}.zip")

            utils.create_zip_of_folder(base_path, output_zip)

            return {
                "message": "FastAPI Code is successfully Generated with Files and Folder Structure.",
                "folder_path": base_path,
                "zip_path": output_zip
                
            }
        
        elif framework_test_cases == "Django":

            base_path = os.getenv("BACKEND_BASE_FOLDER") + "/Code_folder"
            
            base_path = create_unique_folder(base_path, unique_id)

            user_story_filter_template = prompt_templates.user_story_filter_template.format(user_story_accpt_criet = user_story_acceptance_criteria)
            logger.info("Processing the User story and acceptance criteria to make it detailed and arranged ...")

            user_story_accpt_criet = get_conversation_openai(template = user_story_filter_template)
            logger.info("Successfully processed the User story and acceptance criteria.")

            logger.info("Generating the API contract for the User story and acceptance criteria ...")
            api_contract_gen_template = prompt_templates.api_contract_gen_template.format(user_story_accpt_criet = user_story_accpt_criet)

            api_contract = utils.replace_braces(get_conversation_openai(template = api_contract_gen_template))

            logger.info("Successfully generated the API contract for the User story and acceptance criteria.")

            logger.info("Writting the API contract in Markdown(.md) file ...")

            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.md"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_markdown_file(full_path, api_contract)

            logger.info("Writting the API contract in Word(.docx) file ...")

            # Specify the file name for the Markdown file
            file_name = "Gen_api_contract.docx"  # Ensure you have permissions to write to the desired folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_word_file(full_path, api_contract)

            django_code_gen_template = prompt_templates.django_code_gen_template.format(user_story_accpt_criet = user_story_accpt_criet, api_contract = api_contract)
            
            logger.info("Generating Code for the User story and acceptance criteria according to the API contract ...")

            gen_code = get_conversation_openai(template = django_code_gen_template)

            logger.info("Successfully generated Code for the User story and acceptance criteria according to the API contract.")   

            # Specify the file name and path
            file_name = "Gen_code.txt"  # Writing to the root folder

            # Combine the base path with the file name to get the full path
            full_path = os.path.join(base_path, file_name)

            write_text_file(full_path, gen_code)

            logger.info("Improving the Code Quality of the Generated Code making it well commented also adding Documentation ...")
            
            improved_gen_code = improve_code_snippet(gen_code, base_path)
            
            code_insertion(improved_gen_code, base_path)

            output_zip = os.getenv("BACKEND_BASE_FOLDER") + "/Zip_folder/"
            
            # Creates a 32-character hexadecimal string & Update base_path to point to the new unique folder
            output_zip = os.path.join(output_zip, f"{unique_id}.zip")

            utils.create_zip_of_folder(base_path, output_zip)

            return {
                "message": "Django Code is successfully Generated with Files and Folder Structure.",
                "folder_path": base_path, 
                "zip_path": output_zip
            }

    except Exception as e:
        logger.exception(f"HTTP Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-zip/",  summary="Download zip file")
async def download_zip(file_path: str) -> JSONResponse:
    """
    Download a zip file from the given file path and return its Base64 encoded content.

    Args:
        file_path (str): The absolute or relative path to the zip file on the server.

    Returns:
        JSONResponse: A JSON response containing:
            - content (str): The Base64 encoded content of the zip file.
            - message (str): A message indicating successful encoding.
            - size (int): The size of the original file in bytes.

    Raises:
        HTTPException: If the file cannot be accessed due to permissions, 
                       or any other unexpected error occurs.
    """
    try:
        # Open the zip file in binary mode for reading.
        with open(file_path, "rb") as file:
            zip_content: bytes = file.read()

        # Encode the binary content to a Base64 string.
        zip_base64: str = base64.b64encode(zip_content).decode("utf-8")

        # Return a successful JSON response with the encoded content and file size.
        return JSONResponse(
            status_code=200,
            content={
                "content": zip_base64,
                "message": "File encoded successfully",
                "size": len(zip_content)
            }
        )

    except HTTPException as e:
        # Log the error and re-raise already handled HTTP exceptions.
        logger.exception(f"HTTP Exception: {e.detail}")
        raise

    except PermissionError as e:
        # Log the permission error and raise an HTTP 403 Forbidden error.
        logger.exception(f"Permission Error: {e}")
        raise HTTPException(
            status_code=403,
            detail="Permission denied for file access"
        )

    except Exception as e:
        # Log any unexpected error and raise an HTTP 500 Internal Server Error.
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
@app.post("/preview-directory/",  summary="Gives a preview of the directory")
async def preview_directory(directory_path: str) -> JSONResponse:
    """
    Retrieves a preview of the specified directory.

    This endpoint provides details about the contents of a given directory, 
    such as files and subdirectories.

    Args:
        directory_path (str): The absolute or relative path of the directory to preview.

    Returns:
        JSONResponse: A JSON response containing the directory details.

    Raises:
        HTTPException (400): If the request contains invalid data.
        HTTPException (500): If an unexpected error occurs.
    """
    try:
        return get_folder_details(directory_path)

    except HTTPException as he:
        logger.exception(he)
        raise he
    except Exception as e:
        logger.exception(f"Unexpected error: {(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
  