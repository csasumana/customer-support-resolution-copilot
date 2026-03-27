from typing import List, Dict
from app.schemas.ticket import SupportTicket


class PlannerAgent:
    def plan_resolution(
        self,
        ticket: SupportTicket,
        classification: str,
        severity: str,
        retrieved_policies: List[Dict],
    ) -> tuple[str, str]:
        """
        Returns:
            resolution, reason
        """

        if classification in ["fraud_risk", "safety_issue"]:
            return "escalate_to_specialist", "Fraud or safety issues require immediate escalation per policy"

        if classification == "payment_issue":
            if ticket.order_value is not None and ticket.order_value > 100:
                return "escalate_to_specialist", "High-value payment dispute requires escalation"
            return "ask_for_more_info", "Need payment verification details before issuing refund"

        if classification == "wrong_item":
            return "replacement", "Wrong item issues should prefer replacement when feasible"

        if classification == "missing_item":
            if ticket.prior_issues_count >= 3:
                return "partial_refund", "Repeated issues favor faster customer recovery via partial refund"
            if ticket.order_value is not None and ticket.order_value <= 25:
                return "partial_refund", "Low-value missing item is best handled via partial refund"
            return "replacement", "Missing item may be resolved via replacement if feasible"

        if classification == "delivery_delay":
            if (
                ticket.promised_eta_minutes is not None
                and ticket.actual_eta_minutes is not None
                and (ticket.actual_eta_minutes - ticket.promised_eta_minutes) > 60
            ):
                return "partial_refund", "Delivery delay exceeds policy threshold for compensation"
            return "apology_and_close", "Minor delay can be handled with apology"

        if classification == "refund_request":
            return "ask_for_more_info", "Refund requested without sufficient issue classification"

        return "apology_and_close", "General complaint resolved with apology and closure"