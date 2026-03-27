from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Customer Support Resolution Copilot",
    description="LangGraph-based agentic AI workflow for ticket triage, policy retrieval, resolution planning, and action orchestration",
    version="1.0.0",
)

app.include_router(router)