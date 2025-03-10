import pandas as pd
from io import BytesIO
from fastapi import FastAPI, HTTPException
from Logging_folder.logger_file import logger

async def excel_sheet_processing(excel_file):
    """
    Processes an uploaded Excel file and extracts its content row by row.
    
    The function reads an Excel file, validates its format, and converts all cell values to strings.
    It then concatenates the values of each row into a single string with a separator and returns 
    the aggregated text.
    
    Parameters:
    excel_file (UploadFile): The uploaded Excel file in .xlsx or .xls format.
    
    Returns:
    str: A formatted string containing the extracted content from the Excel file.
    
    Raises:
    HTTPException: If the file type is invalid or an error occurs during processing.
    """
    # Validate file type (only allow .xlsx and .xls files)
    if not excel_file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files accepted.")
    
    try:
        # Read file contents asynchronously
        contents = await excel_file.read()
        
        # Load Excel file into a Pandas DataFrame, treating all columns as strings to avoid NaN issues
        df = pd.read_excel(BytesIO(contents), dtype=str)
        
        # Initialize a string to store extracted content
        user_story_acceptance_criteria = ""
        
        # Iterate through each row in the DataFrame
        for _, row in df.iterrows():
            # Convert all values to strings, replacing NaN with '[Missing]', and join with a separator
            row_content = " | ".join(row.astype(str).fillna("[Missing]"))
            
            # Append formatted row content to the result string
            user_story_acceptance_criteria += row_content + "\n"
        
        return user_story_acceptance_criteria
    
    except Exception as e:
        # Log the exception and return an HTTP error response
        logger.exception("Error processing Excel file: %s", e)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")