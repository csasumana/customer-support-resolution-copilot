from pydantic import BaseModel, Field
from typing import Optional, List


class SupportTicket(BaseModel):
    ticket_id: str = Field(..., description="Unique support ticket ID")
    customer_message: str = Field(..., description="Raw customer complaint or issue description")
    order_id: Optional[str] = Field(default=None, description="Associated order ID if available")
    order_value: Optional[float] = Field(default=None, description="Order value in USD or normalized currency")
    customer_id: Optional[str] = Field(default=None, description="Unique customer ID if available")
    prior_issues_count: int = Field(default=0, description="Number of recent prior issues for this customer")
    promised_eta_minutes: Optional[int] = Field(default=None, description="Promised delivery ETA in minutes")
    actual_eta_minutes: Optional[int] = Field(default=None, description="Actual delivery ETA in minutes")
    tags: List[str] = Field(default_factory=list, description="Optional pre-existing tags")