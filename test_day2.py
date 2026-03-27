from pprint import pprint
from app.schemas.ticket import SupportTicket
from app.agents.workflow import SupportWorkflow


def run_ticket(ticket: SupportTicket):
    workflow = SupportWorkflow()
    result = workflow.run(ticket)

    print("\n" + "=" * 80)
    print(f"TICKET ID: {ticket.ticket_id}")
    print("=" * 80)

    print("\n--- INPUT TICKET ---")
    pprint(ticket.model_dump())

    print("\n--- CLASSIFICATION ---")
    print(result["classification"])

    print("\n--- SEVERITY ---")
    print(result["severity"])

    print("\n--- RETRIEVED POLICIES ---")
    for policy in result["retrieved_policies"]:
        print(f"- {policy['name']} (score={policy['score']:.4f})")

    print("\n--- RESOLUTION ---")
    print(result["resolution"])

    print("\n--- CUSTOMER RESPONSE ---")
    print(result["customer_response"])

    print("\n--- ACTIONS ---")
    for action in result["actions"]:
        print(f"- {action}")

    print("\n--- ACTION TRACE ---")
    for trace in result["trace"]:
        pprint(trace)


def main():
    # Ticket 1: delayed + missing item
    ticket_1 = SupportTicket(
        ticket_id="TICKET_101",
        customer_message="My order was delayed by 90 minutes and one item was missing. I want a refund.",
        order_id="ORDER_101",
        order_value=18.5,
        customer_id="CUST_101",
        prior_issues_count=1,
        promised_eta_minutes=30,
        actual_eta_minutes=120,
    )

    # Ticket 2: payment issue high value
    ticket_2 = SupportTicket(
        ticket_id="TICKET_102",
        customer_message="I was charged twice for my order and this is a payment issue. Please help immediately.",
        order_id="ORDER_102",
        order_value=145.0,
        customer_id="CUST_102",
        prior_issues_count=0,
    )

    # Ticket 3: safety issue
    ticket_3 = SupportTicket(
        ticket_id="TICKET_103",
        customer_message="The delivery person behaved in an unsafe and threatening way. I want to report this.",
        order_id="ORDER_103",
        order_value=22.0,
        customer_id="CUST_103",
        prior_issues_count=0,
    )

    run_ticket(ticket_1)
    run_ticket(ticket_2)
    run_ticket(ticket_3)


if __name__ == "__main__":
    main()