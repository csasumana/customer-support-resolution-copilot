from typing import TypedDict, List, Optional, Dict, Any
from app.schemas.ticket import SupportTicket


class SupportAgentState(TypedDict):
    ticket: SupportTicket
    classification: Optional[str]
    severity: Optional[str]
    retrieved_policies: List[Dict[str, Any]]
    resolution: Optional[str]
    customer_response: Optional[str]
    actions: List[str]
    trace: List[Dict[str, Any]]