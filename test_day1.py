from app.schemas.ticket import SupportTicket
from app.retrieval.policy_retriever import PolicyRetriever
from app.tools.logging_tools import log_action


def main():
    ticket = SupportTicket(
        ticket_id="TICKET_001",
        customer_message="My order was delayed by 90 minutes and one item was missing. I want a refund.",
        order_id="ORDER_123",
        order_value=18.5,
        customer_id="CUST_001",
        prior_issues_count=1,
        promised_eta_minutes=30,
        actual_eta_minutes=120,
    )

    retriever = PolicyRetriever()
    results = retriever.retrieve(ticket.customer_message, top_k=2)

    trace = []
    log_action(
        trace,
        step="retrieval",
        decision="retrieved_top_2_policies",
        reason=f"Retrieved {[r['name'] for r in results]} based on semantic similarity",
    )

    print("\n=== TICKET ===")
    print(ticket.model_dump())

    print("\n=== RETRIEVED POLICIES ===")
    for idx, result in enumerate(results, start=1):
        print(f"\nPolicy {idx}: {result['name']}")
        print(f"Score: {result['score']:.4f}")
        print(result["text"][:300])

    print("\n=== ACTION TRACE ===")
    for item in trace:
        print(item)


if __name__ == "__main__":
    main()