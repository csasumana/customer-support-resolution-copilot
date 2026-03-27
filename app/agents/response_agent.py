from app.schemas.ticket import SupportTicket


class ResponseAgent:
    def generate_response(
        self,
        ticket: SupportTicket,
        resolution: str,
        classification: str,
    ) -> tuple[str, str]:
        """
        Returns:
            customer_response, reason
        """

        if resolution == "escalate_to_specialist":
            return (
                "We’re sorry for the inconvenience. Your issue requires specialist review, and our team has escalated it for priority handling. We’ll follow up with you shortly.",
                "Escalation response generated",
            )

        if resolution == "ask_for_more_info":
            return (
                "We’re sorry for the inconvenience. To help resolve this quickly, could you please share any additional details such as payment confirmation, item details, or a screenshot if available?",
                "Requested more information from customer",
            )

        if resolution == "replacement":
            return (
                "We’re sorry for the inconvenience. We’ve initiated a replacement request for the affected item(s), and our team will keep you updated on the next steps.",
                "Replacement response generated",
            )

        if resolution == "full_refund":
            return (
                "We’re sorry for the inconvenience. We’ve approved a full refund for this issue. The amount should reflect within 5 business days depending on your payment method.",
                "Full refund response generated",
            )

        if resolution == "partial_refund":
            if classification == "delivery_delay":
                return (
                    "We’re sorry for the inconvenience caused. Based on the issue reported, we’re issuing a partial refund for this order.",
                    "Delay compensation response generated",
                )
            return (
                "We’re sorry for the inconvenience. We’ve approved a partial refund for the affected item(s). The refund should reflect within 5 business days depending on your payment method.",
                "Partial refund response generated",
            )

        return (
            "We’re sorry for the inconvenience caused. Thank you for reporting this issue. Our team has noted the concern and we appreciate your patience.",
            "Apology and close response generated",
        )