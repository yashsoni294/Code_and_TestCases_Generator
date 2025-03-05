from docx import Document
from Logging_folder.logger_file import logger
import re
import os
from Model_calling.openai_calling import get_conversation_openai
from Templates import prompt_templates

def write_markdown_file(full_path: str, api_contract: str) -> None:
    """
    Writes the API contract to a Markdown file at the specified path.
    Parameters:
    - full_path: The complete path where the Markdown file will be written.
    - api_contract: The content to be written to the file.

    Returns:
    None

    Notes:
    - If there is a permission issue, a PermissionError is caught and logged.
    - Other exceptions are also caught and logged.
    - Uses a logger to log success or error messages.
    """
    # Attempt to write the API contract content to the specified file path
    try:
        # Open the file in write mode and write the api_contract content
        with open(full_path, 'w') as file:
            file.write(api_contract)
        # Log a success message with the file path
        logger.info(f"Successfully written API contract in Markdown(.md) file to {full_path}.")
    
    # Handle permission errors during file writing
    except PermissionError as e:
        # Log the permission error with additional context
        logger.error(f"Permission denied when trying to write to {full_path}. You need elevated privileges. Error: {e}.")
    
    # Handle any other unexpected exceptions
    except Exception as e:
        # Log the exception with the file path and error details
        logger.error(f"An unexpected error occurred while writing to {full_path}: {e}.")

def write_word_file(full_path: str, api_contract: str) -> None:
    """
    Create a Word (.docx) file at the specified path and write the API contract content to it.

    Args:
        full_path (str): The full path where the Word file will be saved.
        api_contract (str): The content to be written to the Word file.

    Notes:
        - Requires the `docx` module to be installed.
        - Logs a success message if the file is written successfully.
        - Logs an error message if there is a permission issue or any other exception occurs.
    """
    try:
        # Initialize a new Word document object
        doc = Document()
        # Add the API contract content as a paragraph to the document
        doc.add_paragraph(api_contract)
        # Save the document to the specified file path
        doc.save(full_path)
        # Log a success message with the file path
        logger.info(f"Successfully written API contract in Word(.docx) file to {full_path}.")
    except PermissionError as e:
        # Handle permission errors, e.g., when the program doesn't have write access to the directory
        logger.error("Permission denied. You need elevated privileges to write to the desired folder. - {e}")
    except Exception as e:
        # Handle any other exceptions that might occur during the process
        logger.error("An unexpected error occurred while writing the Word file. - {e}")

def write_text_file(full_path: str, gen_code: str) -> None:
    """
    Write the provided code/text string to a file at the specified path.

    This function attempts to open a file in write mode using the given full path,
    writes the provided string to the file using UTF-8 encoding, and logs the result.
    If the file is successfully written, an info message is logged. If a PermissionError
    or any other exception occurs, the error is logged accordingly.

    Parameters:
        full_path (str): The complete file path where the text file will be created.
        gen_code (str): The string content (code or text) to write into the file.
    """
    try:
        # Open the file in write mode with UTF-8 encoding.
        with open(full_path, "w", encoding='utf-8') as file:
            # Write the provided content to the file.
            file.write(gen_code)
        
        # Log the success message indicating the file was written.
        logger.info(f"Successfully code written to: {full_path}")
    
    except PermissionError:
        # Log an error if there is a permission issue when writing the file.
        logger.error("Permission denied: You need elevated privileges to write to the root folder.")
    
    except Exception as e:
        # Log any other exception that occurs during the file write operation.
        logger.error(f"An error occurred: {e}")

def improve_code_snippet(gen_code: str, base_path: str) -> str:
    """
    Extracts code snippets with file path annotations from the given generated code,
    improves each code snippet using an external OpenAI conversation, and returns the
    concatenated improved code snippets.

    The input string should contain code snippets formatted as:
        ```<language>
        # <file_path>
        <code_content>
        ```

    Parameters:
        gen_code (str): The generated code string containing one or more code snippets.
        base_path (str): The base directory path to which the file paths in the code snippets are relative.

    Returns:
        str: A string containing all improved code snippets concatenated together.
    """
    # Regular expression to extract code snippets and their file paths.
    # It captures the programming language, file path (commented), and the actual code content.
    pattern = r"```(\w+)\n# (.+?)\n(.*?)```"

    # Find all matches in the input string using DOTALL so that '.' matches newlines.
    matches = re.finditer(pattern, gen_code, re.DOTALL)

    improved_gen_code = ""
    # Iterate through each matched code snippet.
    for match in matches:
        # Extract the programming language (e.g., python, javascript).
        language = match.group(1)
        
        # Extract and clean up the file path.
        file_path = match.group(2).strip()
        # Create the full file path by combining the base path with the relative file path.
        file_path = os.path.join(base_path, file_path)
        
        # Extract and clean up the actual code content.
        code_content = match.group(3).strip()

        # Format the prompt template with the extracted information and pass it to the OpenAI conversation.
        improved_code = get_conversation_openai(
            template=prompt_templates.improve_code_quality_template.format(
                language=language,
                file_path=file_path,
                code_content=code_content,
                input_string=gen_code
            )
        )
        # Append the improved code to the final result.
        improved_gen_code += improved_code

    return improved_gen_code

def code_insertion(improved_gen_code: str, base_path: str) -> None:
    """
    Parses the provided code string for code snippets and inserts them into respective files.

    The function searches for code blocks in the given string using a regular expression pattern.
    Each code block is expected to have the following format:
    
        ```<language>
        # <relative_file_path>
        <code_content>
        ```

    It then creates any necessary directories (if they don't exist) under the provided base path and writes
    the code content to the specified files.

    Parameters:
        improved_gen_code (str): The string containing the generated code with embedded file paths.
        base_path (str): The base directory path where files will be created.

    Returns:
        None
    """
    # Regular expression to extract code snippets and their file paths.
    # The pattern captures:
    #   - group(1): language identifier (e.g., python)
    #   - group(2): relative file path (after a "# " marker)
    #   - group(3): actual code content
    pattern: str = r"```(\w+)\n# (.+?)\n(.*?)```"

    # Iterate through all matches in the input string using DOTALL mode to capture multiline code content.
    matches = re.finditer(pattern, improved_gen_code, re.DOTALL)

    for match in matches:
        language: str = match.group(1)
        file_path: str = match.group(2).strip()
        code_content: str = match.group(3).strip()

        # Combine the base path with the relative file path to get the full file path.
        file_path = os.path.join(base_path, file_path)
        
        # Extract the directory name from the file path.
        dir_name: str = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            try:
                # Create the directory structure if it doesn't exist.
                os.makedirs(dir_name)
            except OSError as e:
                logger.error(f"Error creating directory '{dir_name}': {e}")

        # Write the extracted code content to the file.
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(code_content)
        except Exception as e:
            logger.error(f"Error writing to file '{file_path}': {e}")

    logger.info("Successfully inserted the generated code into the respective files and directories.")

def create_unique_folder(base_path: str, unique_id) -> str:
    """
    Creates a unique folder inside the provided base path.
    
    Parameters:
        base_path (str): The directory where the unique subfolder will be created.
    
    Returns:
        str: The path to the newly created unique folder.
    """
    # Construct the full path to the unique folder
    unique_folder = os.path.join(base_path, unique_id)
    
    # Create the directory (this call will do nothing if it already exists)
    os.makedirs(unique_folder, exist_ok=True)
    
    # Log the unique folder path
    logger.info(f"The unique created folder path is: {unique_folder}")
    
    return unique_folder



def get_folder_details(root_path):
    """
    Traverse a folder structure starting from the given root path and collect 
    the content of text files into a dictionary with file paths as keys.

    Args:
        root_path (str): The root directory path to start the traversal.

    Returns:
        dict: A dictionary where keys are file paths and values are file contents.
    """
    file_contents = {}  # Dictionary to store file paths and their content.

    # Define folder names to exclude
    exclude_folders = {
        "myenv", "venv", "env", ".git", "__pycache__", ".tox", ".idea", ".vscode", "node_modules", "dist", "build", 
        "target", "out", ".cache", "tmp", ".env", ".pytest_cache", ".coverage", ".gradle", ".m2", "vendor", ".nox", 
        ".tox", ".bundle", "CMakeFiles"
    }

    # Define file extensions to skip (image, video, and other non-text files)
    exclude_extensions = {
        ".pdf", ".docx", ".xlsx", ".csv", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg",
        ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpeg", ".mpg", ".3gp", ".mp3", ".wav", ".flac", 
        ".aac", ".ogg", ".wma", ".m4a", ".opus", ".oga", ".weba", ".amr", ".log"
    }

    # Define specific file names to exclude
    exclude_files = {"gen_code.txt", "relavant_files.txt", "prompt_answer.txt"}
                                                                            
    # Traverse the directory structure using os.walk.
    for root, dirs, files in os.walk(root_path):
        # Remove directories that are in the exclude list
        dirs[:] = [d for d in dirs if d not in exclude_folders]

        # Iterate through the files in the current directory.
        for file_name in files:
            file_path = os.path.join(root, file_name)  # Construct the full file path.

            # Skip specific files based on their names.
            if file_name in exclude_files:
                continue  # Skip processing these files.

            # Skip files based on their extensions (image/video files).
            if any(file_name.lower().endswith(ext) for ext in exclude_extensions):
                continue  # Skip non-text files.

            # Attempt to read the file content.
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()  # Read the content of the file.
                    content = content.replace("'", '"')
                    file_contents[file_path] = content # Store content in dictionary.
            except Exception:
                try:
                    with open(file_path, 'r', encoding='utf-16') as file:
                        content = file.read()
                        content = content.replace("'", '"')
                        file_contents[file_path] = content  # Store content in dictionary.
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
    logger.info("Successfully fetched content and file paths from the folders.")
    return file_contents  # Return the collected file content dictionary.
