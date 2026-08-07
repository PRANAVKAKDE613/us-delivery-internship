import os
from fastapi import FastAPI, HTTPException, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from src.triage_agent import triage_ticket, TriageResult
from src.tam_summariser import generate_account_brief, TAMAccountBrief, TAMSummariserEngine

app = FastAPI(
    title="Technical Support & TAM AI Platform API",
    description="Production-grade AI microservices for Intelligent Ticket Triage and TAM Account Health Summarization.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketInputSchema(BaseModel):
    ticket_id: Optional[str] = Field(None, description="Optional ticket ID (e.g. TCK-0001)")
    subject: str = Field(..., description="Ticket subject line", example="[Authentication] SAML SSO login failing with OAuth_401 error")
    body: str = Field(..., description="Free-text ticket body content", example="Users are unable to log in via Okta SAML SSO. Error OAuth_401 invalid client credentials.")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "support-tam-ai-api", "version": "1.0.0"}

@app.post("/api/v1/triage", response_model=TriageResult, summary="Triage Support Ticket (Task 1)")
def triage_endpoint(payload: TicketInputSchema = Body(...)):
    try:
        result = triage_ticket(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/account-brief/{account_id}", response_model=TAMAccountBrief, summary="TAM Account Health Brief (Task 2)")
def account_brief_endpoint(account_id: str = Path(..., description="Target Account ID e.g. ACC-001")):
    """
    Ingests an Account ID, retrieves the account summary and 90-day ticket history,
    and returns a deterministic 3-section brief with direct quote risk justifications.
    """
    try:
        return generate_account_brief(account_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/account-brief/{account_id}/stream", summary="Stream TAM Account Brief (Bonus)")
def stream_account_brief_endpoint(account_id: str = Path(...)):
    """
    Streams the markdown TAM account brief token by token in real-time.
    """
    try:
        engine = TAMSummariserEngine()
        return StreamingResponse(engine.stream_brief(account_id), media_type="text/plain")
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
