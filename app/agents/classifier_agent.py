from app.schemas.ticket import SupportTicket
from app.retrieval.intent_matcher import IntentMatcher


class ClassifierAgent:
    def __init__(self):
        self.intent_matcher = IntentMatcher()

    def classify(self, ticket: SupportTicket):
        message = ticket.customer_message.lower()

        # --------------------------------------------------
        # 1. Critical deterministic overrides
        # --------------------------------------------------
        if any(keyword in message for keyword in [
            "unsafe",
            "threatening",
            "threatened",
            "felt unsafe",
            "harassed",
            "harassment",
            "delivery person was threatening",
        ]):
            return "safety_issue", "critical", "Critical safety language detected"

        if any(keyword in message for keyword in [
            "unauthorized charge",
            "someone used my card",
            "fraud",
            "fraudulent",
            "suspicious charge",
            "account compromised",
        ]):
            return "fraud_risk", "critical", "Fraud-risk language detected"

        # --------------------------------------------------
        # 2. Strong deterministic operational signals first
        #    (to avoid semantic confusion with requested remedies)
        # --------------------------------------------------

        # Delivery delay from structured ETA
        if (
            ticket.promised_eta_minutes is not None
            and ticket.actual_eta_minutes is not None
            and (ticket.actual_eta_minutes - ticket.promised_eta_minutes) > 60
        ):
            return "delivery_delay", "medium", "Delivery delayed by more than 60 minutes"

        # Missing item lexical signals
        if any(keyword in message for keyword in [
            "missing item",
            "item missing",
            "one item missing",
            "item was missing",
            "one item was missing",
            "items were missing",
            "stuff is missing",
            "something is missing",
            "missing from my order",
            "part of my order is missing",
        ]):
            severity = "high" if ticket.prior_issues_count >= 2 else "medium"
            reason = "Repeated prior issues" if severity == "high" else "Missing item issue detected"
            return "missing_item", severity, reason

        # Wrong item lexical / pattern signals
        if any(keyword in message for keyword in [
            "wrong item",
            "wrong order",
            "got the wrong item",
            "received the wrong item",
            "got the wrong food",
        ]):
            return "wrong_item", "medium", "Wrong item issue detected"

        if "asked for" in message and "but got" in message:
            return "wrong_item", "medium", "Detected substitution-style wrong item complaint"

        # Payment issue lexical signals
        if any(keyword in message for keyword in [
            "charged twice",
            "double charged",
            "billed twice",
            "payment issue",
            "payment failed",
            "charged my card",
            "charged but order failed",
            "order didn’t go through",
            "order didn't go through",
        ]):
            severity = "high" if ticket.order_value >= 100 else "medium"
            reason = "High-value order" if severity == "high" else "Payment issue detected"
            return "payment_issue", severity, reason

        # --------------------------------------------------
        # 3. Semantic issue classification (NOT refund_request)
        # --------------------------------------------------
        best_intent, best_score, all_scores = self.intent_matcher.match_intent(ticket.customer_message)

        if best_score < 0.45:
            return "general_complaint", "low", f"Low-confidence semantic match (score={best_score:.4f})"

        severity = self._determine_severity(ticket, best_intent)

        reason = (
            f"Semantic issue match -> {best_intent} "
            f"(score={best_score:.4f}, top_scores={all_scores})"
        )

        return best_intent, severity, reason

    def _determine_severity(self, ticket: SupportTicket, classification: str) -> str:
        if classification == "delivery_delay":
            if (
                ticket.promised_eta_minutes is not None
                and ticket.actual_eta_minutes is not None
                and (ticket.actual_eta_minutes - ticket.promised_eta_minutes) > 60
            ):
                return "medium"
            return "low"

        if classification in ["missing_item", "wrong_item"]:
            return "high" if ticket.prior_issues_count >= 2 else "medium"

        if classification == "payment_issue":
            return "high" if ticket.order_value >= 100 else "medium"

        if classification == "general_complaint":
            return "low"

        return "medium"