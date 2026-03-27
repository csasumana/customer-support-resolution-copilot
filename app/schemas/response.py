from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class TraceEntry(BaseModel):
    step: str
    decision: str
    reason: Optional[str] = None


class SupportAgentResponse(BaseModel):
    ticket_id: str
    classification: str
    severity: str
    retrieved_policies: List[str]
    resolution: str
    customer_response: str
    actions: List[str]
    trace: List[Dict[str, Any]]