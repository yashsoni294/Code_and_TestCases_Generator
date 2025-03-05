import os
import shutil
import re
import openpyxl
from Logging_folder.logger_file import logger
from typing import List, Tuple

def create_zip_of_folder(folder_path: str, output_zip_path: str) -> None:
    """
    Create a ZIP archive of the specified folder.

    This function compresses the folder located at `folder_path` into a ZIP file
    at the location specified by `output_zip_path`. If the output directory does not
    exist, it will be created.

    Parameters:
        folder_path (str): The path to the folder to be zipped.
        output_zip_path (str): The full path (including the .zip extension) where the
                               ZIP file will be created.

    Returns:
        None
    """
    # Extract the directory part of the output path.
    output_dir = os.path.dirname(output_zip_path)
    # Create the output directory if it is specified and doesn't already exist.
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Remove the file extension from the output path to get the base name.
    base_name = os.path.splitext(output_zip_path)[0]
    
    # Determine the parent directory of the folder to be zipped.
    root_dir = os.path.dirname(folder_path)
    # Extract the name of the folder to be zipped.
    base_dir = os.path.basename(folder_path)
    
    # Create the ZIP archive using the base name, specifying the format and the folder.
    shutil.make_archive(base_name, 'zip', root_dir, base_dir)

def extract_test_cases(markdown_text: str) -> List[Tuple[str, str, str, str, str, str, str, str, str, str, str]]:
    """
    Extract test case details from a markdown table.

    This function uses a regular expression to parse a markdown table containing test cases.
    Each row in the table is expected to follow a specific format with fields separated by '|' characters.
    The regex captures the test case identifier (expected in the format 'TC_<number>') and additional fields.

    Args:
        markdown_text (str): The markdown content containing the test cases table.

    Returns:
        List[Tuple[str, str, str, str, str, str, str, str, str, str, str]]:
            A list of tuples, where each tuple corresponds to a row in the table.
            The tuple contains the test case ID and the subsequent fields as strings.
    """
    # Regex pattern to match a table row with the expected format.
    # It captures 11 groups: the first for the test case identifier (TC_...) 
    # and the following 10 for the remaining fields.
    pattern = (
        r"\|\s*(TC_\d+)\s*\|"
        r"\s*([^|]+)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
    )
    
    # Find all matches in the markdown text.
    # The re.DOTALL flag allows the '.' to match newline characters.
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    return matches

def write_to_excel(test_cases: List[Tuple[str, ...]], file_name: str) -> None:
    """
    Write test case data to an Excel file.

    This function creates a new Excel workbook, sets up a worksheet titled "Test Cases",
    writes a header row, appends the provided test case rows, and then saves the workbook to a file.

    Args:
        test_cases (List[Tuple[str, ...]]): A list of tuples where each tuple represents a test case.
            Each tuple should contain the following fields:
            "Test Case ID", "Module", "User Story", "Sub Module",
            "Test Case Description", "Prerequisites", "Test Case Type",
            "Test Steps", "Automation", "Test Data", "Expected Result".
        file_name (str): The file name (and path, if applicable) for the Excel file to be saved.

    Returns:
        None
    """
    # Create a new Excel workbook and get the active worksheet.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    # Define the header row for the Excel sheet.
    headers = [
        "Test Case ID", "Module", "User Story", "Sub Module",
        "Test Case Description", "Prerequisites", "Test Case Type",
        "Test Steps", "Automation", "Test Data", "Expected Result"
    ]
    # Append the header row to the worksheet.
    ws.append(headers)

    # Append each test case row to the worksheet.
    for case in test_cases:
        # Convert the tuple to a list before appending.
        ws.append(list(case))

    # Save the Excel workbook to the specified file.
    wb.save(file_name)
    logger.info(f"Test cases written to {file_name} successfully.")

def replace_braces(input_string: str) -> str:
    """
    Replaces all occurrences of '{' with '[' and '}' with ']' in the input string.

    This function ensures that the input is treated as a string, performs the brace 
    replacement, and returns the modified string.

    Parameters:
        input_string (str): The string to process.

    Returns:
        str: The modified string with replacements.
    """
    # Ensure the input is a string by type casting.
    input_string = str(input_string)
    
    # Replace all occurrences of '{' with '['.
    modified_string = input_string.replace('{', '[')
    
    # Replace all occurrences of '}' with ']'.
    modified_string = modified_string.replace('}', ']')
    
    # Return the modified string, ensuring the output is of type str.
    return str(modified_string)