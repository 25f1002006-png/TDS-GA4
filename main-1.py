import uvicorn
import re
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Initialize the FastAPI app
app = FastAPI(
    title="TechNova Digital Assistant API",
    description="Routes templatized queries to internal functions."
)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows the API to be called from any web frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    # UPDATED: Allow "*" which includes GET, POST, OPTIONS, etc.
    # This is necessary to handle browser "preflight" OPTIONS requests.
    allow_methods=["*"],  
    allow_headers=["*"],  # Allows all headers
)

# Define the regex patterns and their corresponding function handlers.
# Each tuple contains: (compiled_regex, function_name, argument_extractor_lambda)
QUERY_PATTERNS = [
    # 1. Ticket Status: "What is the status of ticket 83742?"
    (
        re.compile(r"What is the status of ticket (\d+)\?"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    
    # 2. Schedule Meeting: "Schedule a meeting on 2025-02-15 at 14:00 in Room A."
    (
        re.compile(r"Schedule a meeting on ([\d-]+) at ([\d:]+) in (.+)\."),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    
    # 3. Expense Balance: "Show my expense balance for employee 10056."
    (
        re.compile(r"Show my expense balance for employee (\d+)\."),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    
    # 4. Performance Bonus: "Calculate performance bonus for employee 10056 for 2025."
    (
        re.compile(r"Calculate performance bonus for employee (\d+) for (\d+)\."),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    
    # 5. Office Issue: "Report office issue 45321 for the Facilities department."
    (
        re.compile(r"Report office issue (\d+) for the ([\w\s]+) department\."),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    )
]

@app.get("/execute")
async def execute_query(q: str = Query(..., description="The user's natural language query.")):
    """
    Analyzes the query string 'q' to find a matching function and extracts its parameters.
    Returns a JSON structure compatible with OpenAI's function calling.
    """
    
    # Iterate through the predefined patterns
    for pattern, func_name, arg_extractor in QUERY_PATTERNS:
        match = pattern.match(q)
        
        if match:
            # If a match is found, extract arguments using the lambda
            try:
                arguments = arg_extractor(match)
                
                # Return the response in the specified format
                # 'arguments' must be a JSON string
                return {
                    "name": func_name,
                    "arguments": json.dumps(arguments)
                }
            except Exception as e:
                # Handle potential errors during argument extraction (e.g., type conversion)
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error processing query: {e}"}
                )

    # If no pattern matches the query
    return JSONResponse(
        status_code=404,
        content={
            "name": "unknown_function",
            "arguments": "{}",
            "error": "Query did not match any known function template."
        }
    )