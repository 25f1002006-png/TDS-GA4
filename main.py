import uvicorn
import re
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="TechNova Digital Assistant API",
    description="Routes templatized queries to internal functions."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This list is now expanded to handle all 30 templates.
# The regex patterns are anchored with `$` to ensure they match the full string.
QUERY_PATTERNS = [
    # --- get_ticket_status ---
    (
        re.compile(r"Ticket (\d+) status\?$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"Status update for ticket (\d+)$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"Update on ticket (\d+), please\.$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"Check ticket (\d+) status now\.$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"Ticket (\d+): current status\.$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"What's the status of ticket (\d+)\?$"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),

    # --- schedule_meeting ---
    (
        re.compile(r"Book meeting on ([\d-]+) at ([\d:]+) in (.+)\.$"),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    (
        re.compile(r"Arrange meeting ([\d-]+), ([\d:]+), room: (.+)$"),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    (
        re.compile(r"Set meeting for ([\d-]+), ([\d:]+) at (.+)\.$"),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    (
        re.compile(r"([\d-]+) meeting at ([\d:]+) in (.+)$"),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    (
        re.compile(r"Schedule meeting on ([\d-]+) in (.+) at ([\d:]+)\.$"),
        "schedule_meeting",
        # Note the re-ordered groups in the lambda!
        lambda m: {"date": m.group(1), "time": m.group(3), "meeting_room": m.group(2)}
    ),
    (
        re.compile(r"Organize meeting ([\d-]+) ([\d:]+) (.+)$"),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),

    # --- get_expense_balance ---
    (
        re.compile(r"Expense balance for emp (\d+)$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"What is emp (\d+)'s expense balance\?$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"Check expenses for employee (\d+)$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"Show expense status for emp (\d+)$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"Employee (\d+), expense balance\?$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"(\d+) expense balance$"),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),

    # --- calculate_performance_bonus ---
    (
        re.compile(r"Calculate bonus for emp (\d+) in (\d+)$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"Bonus details for employee (\d+) for (\d+)$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"What bonus for emp (\d+) in (\d+)\?$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"Emp (\d+) bonus (\d+)$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"Fetch bonus for emp (\d+) for (\d+)$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"Employee (\d+) performance bonus (\d+)$"),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),

    # --- report_office_issue ---
    (
        re.compile(r"Report office issue (\d+) for (.+)$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
    (
        re.compile(r"Office issue (\d+) in (.+)$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
    (
        re.compile(r"(\d+) reported in (.+) department$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
    (
        re.compile(r"Log issue (\d+) for (.+) dept$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
    (
        re.compile(r"File issue (\d+) in (.+)$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
    (
        re.compile(r"Report: issue (\d+), department (.+)$"),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    ),
]


@app.get("/")
async def root():
    return {"message": "TechNova Digital Assistant API is running."}


@app.get("/execute")
async def execute_query(q: str = Query(..., description="The user's natural language query.")):
    
    # Iterate through the new, expanded list of patterns
    for pattern, func_name, arg_extractor in QUERY_PATTERNS:
        # Use re.fullmatch() to ensure the pattern matches the *entire* query string
        match = re.fullmatch(pattern, q)
        
        if match:
            try:
                arguments = arg_extractor(match)
                
                # The output format (with json.dumps) remains the same
                return {
                    "name": func_name,
                    "arguments": json.dumps(arguments)
                }

            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error processing query: {e}"}
                )

    # If no pattern matches, return the 404 response
    return JSONResponse(
        status_code=404,
        content={
            "name": "unknown_function",
            "arguments": "{}",
            "error": "Query did not match any known function template."
        }
    )
