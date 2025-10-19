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

QUERY_PATTERNS = [
    (
        re.compile(r"What is the status of ticket (\d+)\?"),
        "get_ticket_status",
        lambda m: {"ticket_id": int(m.group(1))}
    ),
    (
        re.compile(r"Schedule a meeting on ([\d-]+) at ([\d:]+) in (.+)\."),
        "schedule_meeting",
        lambda m: {"date": m.group(1), "time": m.group(2), "meeting_room": m.group(3)}
    ),
    (
        re.compile(r"Show my expense balance for employee (\d+)\."),
        "get_expense_balance",
        lambda m: {"employee_id": int(m.group(1))}
    ),
    (
        re.compile(r"Calculate performance bonus for employee (\d+) for (\d+)\."),
        "calculate_performance_bonus",
        lambda m: {"employee_id": int(m.group(1)), "current_year": int(m.group(2))}
    ),
    (
        re.compile(r"Report office issue (\d+) for the ([\w\s]+) department\."),
        "report_office_issue",
        lambda m: {"issue_code": int(m.group(1)), "department": m.group(2)}
    )
]

@app.get("/")
async def root():
    return {"message": "TechNova Digital Assistant API is running."}

@app.get("/execute")
async def execute_query(q: str = Query(..., description="The user's natural language query.")):
    
    for pattern, func_name, arg_extractor in QUERY_PATTERNS:
        match = pattern.match(q)
        
        if match:
            try:
                arguments = arg_extractor(match)
                
                return {
                    "name": func_name,
                    "arguments": json.dumps(arguments)
                }

            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error processing query: {e}"}
                )

    return JSONResponse(
        status_code=404,
        content={
            "name": "unknown_function",
            "arguments": "{}",
            "error": "Query did not match any known function template."
        }
    )
