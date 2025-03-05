api_contract_gen_template = """
    Please provide the API contract for the following user story and acceptance criteria:

    {user_story_accpt_criet}

    The API contract should include the necessary endpoints, request/response formats, and any other relevant details.
    Also add Introduction of the project at the beginning of the documentation. Remember do not rush to generate the 
    code. Take your time to generate a detailed and good quality API contract.

    One example API Endpoin is as below write in the same formate:- 

    VERIFY CONTENT LICENSEES API KEY ENDPOint details 

    CONTENT TYPE -
    The service should be posted (POST) with the following information: 

    HEADERS 

    | Key-Value                                 |
    |----------------|--------------------------|
    | Content-Type   | application/json         |
    | Accept         | application/json,        |

    | Request                                   |
    |----------------|--------------------------|
    | Method  | POST                            |
    | URL     | [base_url]/sig/metadata-by-year | 

    JSON - PAYLOAD 

    [ 

    “api_key”: enter_api_key_here” 

    ]

    RESPONSE-SUCCESS 

    [  

    “statusCode”:200, 

    “message”:”success”, 

    “accessToken”:”access_token_value” 

    “tokenToken”: “bearer” 

    “organizationName”:”organization name value here”, 

    “tokenExpirationDateTime”:” MM/DD/YYYY HH:MM UTC value ” 
    ] 

    The following exceptions are expected based on input data and return response. 

    RESPONSE- Invalid API key 
    [  

    “statusCode”:404, 

    “message”:”Invalid API key” 
    ] 

    RESPONSE- Server Error 

    [  

    “status_code”:500, 

    “message”:”Internal Server Error”, 

    ] 

    Filter SIG content 

    The system should allow content licensees to filter the SIG content based on year, version, language, and 
    scope name.
"""

reactJS_code_gen_template = """
    Generate complete React+TypeScript code implementing ALL user story requirements. Follow these steps:
    1. Analyze EVERY aspect of the user story and acceptance criteria
    2. Identify ALL required components, pages, services, and dependencies
    3. Generate COMPLETE code for each identified element including ALL imports
    4. Ensure STRICT ADHERENCE to the folder structure
    5. Implement EXACT API contract specifications

    Folder structure MUST be followed PRECISELY:
    structure = [
        "frontend_root": [
            ".gitignore": None,
            "package.json": None,
            "package-lock.json": None,
            "README.md": None,
            "vite.config.js": None,  # If using Vite
            "webpack.config.js": None,  # If using Webpack
            ".env": None,
            ".eslintrc.js": None,  # ESLint configuration
            ".prettierrc": None,  # Prettier configuration
            "public": [
                "index.html": None,
                "favicon.ico": None,
                "manifest.json": None,
                "robots.txt": None,
                "assets": [
                    "images": None,
                    "fonts": No
                ]
            ],
            "src": [
                "index.js": None,
                "main.jsx": None,  # If using Vite
                "App.js": None,
                "App.css": None,
                "routes": [
                    "index.js": None,  # Centralized route configuration
                    "ProtectedRoute.js": None  # For private routes
                ],
                "components": [
                    "Button": [
                        "Button.jsx": None,
                         "Button.module.css": None
                    ],
                    "Header": [
                        "Header.jsx": None,
                        "Header.module.css": None
                    ],
                    "Footer": [
                        "Footer.jsx": None,
                        "Footer.module.css": None
                    ],
                    "Sidebar": [
                        "Sidebar.jsx": None,
                        "Sidebar.module.css": None
                    ],
                    "Loader": [
                        "Loader.jsx": None,
                        "Loader.module.css": None
                    ]
                ],
                "pages": [
                    "Home": [
                        "Home.jsx": None,
                        "Home.module.css": None
                    ],
                    "About": [
                        "About.jsx": None,
                        "About.module.css": None
                    ],
                    "Dashboard": [
                        "Dashboard.jsx": None,
                        "Dashboard.module.css": None
                    ],
                    "Login": [
                        "Login.jsx": None,
                        "Login.module.css": None
                    ],
                    "Register": [
                        "Register.jsx": None,
                        "Register.module.css": None
                    ]
                ],
                "context": [
                    "AuthContext.js": None,  # Authentication context
                    "ThemeContext.js": None  # Theme context
                ],
                "hooks": [
                    "useAuth.js": None,
                    "useTheme.js": None
                ],
                "store": [
                    "index.js": None,
                    "slices": [
                        "authSlice.js": None,
                        "userSlice.js": None
                    ]
                ],
                "services": [
                    "api.js": None,
                    "authService.js": None,
                    "userService.js": None
                ],
                "utils": [
                    "constants.js": None,
                    "helpers.js": None,
                    "validations.js": None
                ],
                "styles": [
                    "global.css": None,
                    "theme.css": None
                ],
                "assets": [
                    "images": None,
                    "icons": None
                ],
                "tests": [
                    "setupTests.js": None,
                    "components": [
                        "Button.test.js": None,
                        "Header.test.js": None
                    ],
                    "pages": [
                        "Home.test.js": None
                    ]
                ]
        
        ]
    ]
            
    User Story and Requirements (IMPLEMENT ALL):

    {user_story_accpt_criet}

    API Contract (IMPLEMENT EXACTLY):

    Essential Rules:
    - Generate MINIMUM VIABLE PRODUCT that SATISFIES ALL requirements
    - Create ALL referenced files and dependencies
    - Use STRICT TYPESCRIPT with interfaces for API contracts
    - Include PRACTICAL ERROR HANDLING
    - Add ESSENTIAL UI STATE MANAGEMENT
    - Implement ACTUAL API SERVICE LAYER
    - Include REACT ROUTER integration where needed
    - Add CORE SECURITY PRACTICES (auth tokens, protected routes)
    - Generate ALL REQUIRED CONFIG FILES:
    - Dockerfile with production-optimized build
    - docker-compose.yml with service definitions
    - .env.example with essential variables
    - jest.config.js for testing
    - README.md with setup instructions
    - package.json with ALL dependencies

    {api_contract}

    Remember to add path with # before the  code snnipet. Also the ``` before and after the code snnipet.
    Output Format:
        ```typescript
        # src/services/authService.ts

        import axios from 'axios';
        import type ( AuthResponse, LoginPayload ) from '../types/auth';

        const API_BASE = import.meta.env.VITE_API_BASE;

        export const authService = (
        async login(credentials: LoginPayload): Promise<AuthResponse> (
            try (
            const response = await axios.post(`(API_BASE)/auth/login`, credentials);
            return response.data;
            ) catch (error) (
            throw new Error('Login failed. Please check your credentials.');
            )
        )
        );
        ```
    Remember to follow the output formate strictly
            
    Also create the code for the files and folders which you are Importing in the other files. Remember do not generate any unnecessary text or explanation. only generate detailed and
    good quality React JS with TypeScript Front-End code. Also give the text which is necessary for the other files like requirements.txt, Dockerfile, 
    docker-compose.yml, README.md, .gitignore etc.Remember your task is to write complete code.
    
    """

improve_code_quality_template = """
    I have the following code block with file path included :

    ```{language}
    # {file_path}
    {code_content}
    ```

    Please improve the code quality and make the code well commented and also include docstring. 
    and  provide the improved code block in the same format. Remember do not provide what 
    improvements you have made only provide the improved code block with file path included in the same 
    formate. Remember do not rush to provide the improved code block. Complete the incomplete code block and also 
    add boiler plate code block if you think it is needed. 

    For your reference the above code is from below code base :
            
    {input_string}

    Remember to return the responce in the same format:

    ```language
    # file_path
    improved_code_content
    ```
"""

user_story_filter_template = """
    I have the following user story and acceptance criteria:

    {user_story_accpt_criet}

    your task is understand the user story and also acceptance criteria and make it detailed and in well arranged 
    formate.
"""


test_cases_gen_template = """
    I have the following user story and acceptance criteria:  

    {user_story_accpt_criet}  

    Your role is of a tester. Based on the provided user story and acceptance criteria, you need to write **detailed and comprehensive test cases** to ensure full coverage positive and negative test cases, try to cover more and more negative case scenarios.  

    Include all necessary details that a tester would require to perform the tests. The test cases should encompass the following aspects:  
    1. **Test Case ID**  
    2. **Module**  
    3. **User Story**  
    4. **Sub-Module**  
    5. **Test Case Description**  
    6. **Prerequisites (Preconditions)**  
    7. **Test Case Type** (Positive/Negative)  
    8. **Test Steps**: Write detailed step-by-step instructions for each test case. For example:  
        - Log in to the Admin portal.  
        - Navigate to "Member Management."  
        - Verify that an error message is displayed if no customer data is available.  
    9. **Automation**: Specify if the test case is automatable (Yes/No).
    10. **Test Data**: Provide any necessary test inputs or configurations.  
    11. **Expected Result**: Clearly define the outcome for each test case.  

    Ensure that:  
    - **Maximum test cases** are generated, covering all possible scenarios, including edge and corner cases and positive and negative test cases, try to cover more and more negative case scenarios.  
    - The test cases are aligned with the user story and acceptance criteria.  
    - The scenarios include validations for both functional and non-functional aspects, wherever applicable.  

    you have to return the response in the following markdown format:

    | Test Case ID | Module          | User Story                                                                                                                                               | Sub Module              | Test Case Description                                           | Prerequisites                                         | Test Case Type      | Test Steps                                                                                                        | Automation | Test Data | Expected Result                                                                                             |
    |--------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|---------------------------------------------------------------|-----------------------------------------------------|---------------------|-----------------------------------------------------------------------------------------------------------------|------------|-----------|-------------------------------------------------------------------------------------------------------------|
    | TC_01        | Navbar Options  | As a user, I want to choose between the Dashboard, Member Management, and Upload Excel options, so that I can easily navigate the application.           | Usability Testing       | Validate the usability of the navbar, ensuring clear labels and intuitive navigation. | User logged in; Navbar displayed.                  | Usability           | 1. Log in to the application. 2. Observe the labeling and layout of the navbar. 3. Test for ease of navigation between options. |            | N/A       | The navbar should have clearly labeled options for "Dashboard" "Member Management" and "Upload Excel" allowing for smooth, intuitive navigation. |
    | TC_02        | Navbar Options  |                                                                                                                                                           | Compatibility Testing   | Ensure the Navbar options work across different browsers (Chrome, Firefox, Safari, etc.). | User logged in with different supported browsers (Chrome, Firefox, Safari). | Compatibility       | 1. Log in using different browsers. 2. Test switching between all Navbar options across each browser. 3. Observe any layout or performance issues. |            | N/A       | The Navbar should function smoothly on all supported browsers, with no layout issues or delays while navigating between options. |
    | TC_03        | Navbar Options  |                                                                                                                                                           | Usability Testing (Mobile) | Ensure that the Navbar options are displayed properly on mobile devices and are easy to navigate. | User logged in on mobile devices (Android, iOS).   | Usability (Mobile) | 1. Log in on a mobile device. 2. Check the layout and functionality of the Navbar. 3. Ensure options are easy to click and switch between. |            | N/A       | The Navbar should be fully responsive on mobile devices, with all options clearly visible and easy to navigate using touch input. |

    Generate test cases with the following complexity dimensions:

    1. **Multi-Layer Validation**  
    - Combine UI, API, and database verification in single test cases  
    - Example: "After UI submission, verify API response AND database entry AND cache update"

    2. **Stateful Scenarios**  
    - Create test sequences where subsequent tests depend on previous outcomes  
    - Example: "Test expired session handling after successful payment flow interruption"

    3. **Concurrent Actions**  
    - Design tests requiring parallel user actions  
    - Example: "Simultaneous file uploads from multiple users with same filename"

    4. **Temporal Conditions**  
    - Incorporate time-sensitive validations:  
    - Timezone boundaries (11:59 PM → 12:00 AM transitions)  
    - Cron job interactions  
    - Session timeout race conditions

    5. **Data Matrix Testing**  
    - Create combinatorial test tables for input parameters  
    - Example: "Test all country-specific date formats with different currency symbols"

    6. **Failure Propagation**  
    - Chain of failure scenarios:  
    - API failure → DB deadlock → UI error handling  
    - Distributed transaction rollbacks

    7. **Security Depth**  
    - Include OWASP Top 10 scenarios with exploit simulations:  
    - SQLi → XSS → CSRF chained attacks  
    - JWT token manipulation  
    - Rate limiting bypass attempts

    8. **Environmental Chaos**  
    - Network latency spikes during file uploads  
    - Disk space exhaustion while processing transactions  
    - DNS failure during OAuth handshake

    9. **Boundary Overflows**  
    - Extreme value testing with scientific notation  
    - 10MB → 10GB → 10TB file size progression  
    - Deep nested JSON structures (10+ levels)

    10. **Permission Ladder**  
        - Vertical and horizontal privilege escalation attempts:  
        - User → Admin → Super Admin role jumping  
        - Cross-tenant data access attempts

    **Enhanced Negative Testing Requirements:**  
    - 50% negative cases minimum  
    - Each negative case must include 3+ failure points  
    - Include "never supposed to happen" scenarios  
    - Test error message specificity (must match exact failure reason)

    **Example Complex Test Case:**  
    | TC_45 | Payment Gateway | Process transactions | Fraud Detection | Simultaneous duplicate transactions across regions | 1. VPN configured 2. Multiple payment profiles 3. Clock sync tool | Negative | 1. Initiate payment from US IP 2. Simultaneously repeat payment from EU IP via VPN 3. Monitor fraud detection system logs 4. Check database locking mechanism | Yes | USD 9999.99, EUR 9999.99 | System should: 1. Block second transaction 2. Flag account for review 3. Generate audit trail 4. Send fraud alert email |

    **Validation Depth Requirements:**  
    1. UI Layer: Visual + Accessibility checks  
    2. API Layer: Response headers + body + status codes  
    3. DB Layer: Data integrity + transaction logs  
    4. Security Layer: Penetration test results  
    5. Performance Layer: Response time metrics

    **Special Scenarios:**  
    - "Airplane mode" testing for mobile apps  
    - Browser DevTools manipulation detection  
    - Certificate pinning bypass attempts  
    - Biometric authentication spoofing 
                
"""

fastapi_code_gen_template = """
    Remember do not rush to generate the code. Take your time to generate a detailed and good quality and error free 
    code. You are a FastAPI Back-End code genrator that generate a detailed and good quality FastAPI Back-End code 
    and the folder structure which we are using is as follows :

    structure = [
    "project_root": [
        "app": [
            "api": [
                "__init__.py": None,
                "v1": [
                    "__init__.py": None,
                    "endpoints": [
                        "__init__.py": None,
                        "user.py": None,
                        "auth.py": None,
                        "other_endpoints.py": None,
                    ]
                ]
            ],
            "core": [
                "__init__.py": None,
                "config.py": None,
                "security.py": None,
                "dependencies.py": None,
            ],
            "models": [
                "__init__.py": None,
                "user.py": None,
                "other_models.py": None,
            ],
            "schemas": [
                "__init__.py": None,
                "user.py": None,
                "other_schemas.py": None,
            ],
            "crud": [
                "__init__.py": None,
                "user.py": None,
                "other_crud.py": None,
            ],
            "db": [
                "__init__.py": None,
                "base.py": None,
                "session.py": None,
                "migrations": "(Generated by Alembic)"
            ],
            "tests": [
                "__init__.py": None,
                "test_api": [
                    "__init__.py": None,
                    "test_user.py": None,
                    "test_auth.py": None,
                ]
            ],
            "main.py": None,
        ],
        "scripts": [
            "create_superuser.py": None,
            "initialize_db.py": None,
        ],
        "requirements.txt": None,
        ".env": None,
        ".env.example": None,
        "Dockerfile": None,
        "docker-compose.yml": None,
        "README.md": None,
        ".gitignore": None,
    ]]
    
    Write a detailed and good quality FastAPI Back-End code for the below user story and acceptance criteria:

    {user_story_accpt_criet}

    and its api contract should be as follows:

    {api_contract}

    Remember to add path before the  code snnipet and also the ``` before and after the code snnipet. 
    For example:
        ```python
        # project_root/app/schemas/user.py

        from pydantic import BaseModel

        class UserLogin(BaseModel):
            username: str
            password: str

        class UserResponse(BaseModel):
            access_token: str
            token_type: str
        ```
    
    Also create the code for the files and folders which you are Importing in the other files. For example Data Base,
    and Models folders etc.  Remember do not generate any unnecessary text or explanation. only generate detailed and
    good quality code. Also give the text which is necessary for the other files like requirements.txt, Dockerfile, 
    docker-compose.yml, README.md, .gitignore etc.Remember your task is to write complete code.
    """

django_code_gen_template = """
    Remember do not rush to generate the code. Take your time to generate a detailed and good quality and error free 
    code. You are a Django Back-End code genrator that generates a detailed and good quality Django Back-End code and 
    the folder structure which we are using is as follows :

    structure = [
    "project_root": [
        "manage.py": None,
        "requirements.txt": None,
        ".env": None,
        ".gitignore": None,
        "README.md": None,
        "Dockerfile": None,
        "docker-compose.yml": None,
        "project_name": [
            "__init__.py": None,
            "asgi.py": None,
            "settings.py": None,
            "urls.py": None,
            "wsgi.py": None,
            "apps": [
                "app_name": [
                    "__init__.py": None,
                    "admin.py": None,
                    "apps.py": None,
                    "forms.py": None,
                    "models.py": None,
                    "urls.py": None,
                    "views.py": None,
                    "serializers.py": None,
                    "tasks.py": None,
                    "tests.py": None,
                    "signals.py": None,
                    "templates": [
                        "app_name": [
                            "*.html": None
                        ]
                    ],
                    "static": [
                        "css": None,
                        "js": None,
                        "images": None,
                        "fonts": None
                    ]
                ]
            ],
            "staticfiles": None
        ],
        "media": [
            "uploads": None
        ],
        "templates": [
            "base.html": None
        ],
        "static": [
            "css": None,
            "js": None,
            "images": None,
            "fonts": None
        ],
        "logs": [
            "django.log": None
        ],
        "scripts": [
            "manage_tasks.py": None
        ],
        "tests": [
            "__init__.py": None,
            "test_project.py": None
            ]
        ]
    ]
    
    Write a detailed and good quality Django Back-End code for the below user story and acceptance criteria:

    {user_story_accpt_criet}

    and its api contract should be as follows:

    {api_contract}

    Remember to add path before the  code snnipet. Also the ``` before and after the code snnipet.
    For example:
        ```python
        # project_root/app/schemas/user.py

        from pydantic import BaseModel

        class UserLogin(BaseModel):
            username: str
            password: str

        class UserResponse(BaseModel):
            access_token: str
            token_type: str
        ```
    
    Also create the code for the files and folders which you are Importing in the other files. For example Data Base,
    and Models folders etc.  Remember do not generate any unnecessary text or explanation. only generate detailed and
    good quality Django Back-End code. Also give the text which is necessary for the other files like requirements.txt, Dockerfile, 
    docker-compose.yml, README.md, .gitignore etc.Remember your task is to write complete code.
    """
