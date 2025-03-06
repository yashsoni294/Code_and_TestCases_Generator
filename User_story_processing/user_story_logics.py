import pandas as pd
from io import BytesIO
from fastapi import FastAPI, HTTPException
from Logging_folder.logger_file import logger

async def excel_sheet_processing(excel_file):
    # Validate file type
    if not excel_file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files accepted.")
        
    try:
        contents = await excel_file.read()
        df = pd.read_excel(BytesIO(contents), dtype=str)  # Read all columns as strings to avoid NaN issues
            
        # Initialize text to hold extracted content
        user_story_acceptance_criteria = ""

        # Iterate through each row
        for _, row in df.iterrows():
            row_content = " | ".join(row.astype(str).fillna("[Missing]"))  # Join all column values with a separator
            user_story_acceptance_criteria += row_content + "\n"
        
        return user_story_acceptance_criteria
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")