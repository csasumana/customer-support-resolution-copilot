from app.schemas.ticket import SupportTicket


class ActionAgent:
    def generate_actions(
        self,
        ticket: SupportTicket,
        classification: str,
        severity: str,
        resolution: str,
    ) -> tuple[list[str], str]:
        """
        Returns:
            actions, reason
        """

        actions = []

        # Queue assignment
        if classification in ["fraud_risk", "payment_issue"]:
            actions.append("assign_queue:payments_risk_team")
        elif classification == "safety_issue":
            actions.append("assign_queue:safety_ops_team")
        elif classification in ["missing_item", "wrong_item", "delivery_delay"]:
            actions.append("assign_queue:delivery_support_team")
        else:
            actions.append("assign_queue:general_support_team")

        # Priority
        actions.append(f"set_priority:{severity}")

        # Resolution-specific actions
        if resolution == "escalate_to_specialist":
            actions.append("create_followup_task:specialist_review")
        elif resolution == "replacement":
            actions.append("create_replacement_request")
        elif resolution == "full_refund":
            actions.append("initiate_full_refund")
        elif resolution == "partial_refund":
            actions.append("initiate_partial_refund")
        elif resolution == "ask_for_more_info":
            actions.append("request_additional_customer_details")
        elif resolution == "apology_and_close":
            actions.append("mark_for_soft_close")

        # Always create internal note
        actions.append("create_internal_ticket_note")

        return actions, "Generated operational actions based on classification, severity, and resolution"