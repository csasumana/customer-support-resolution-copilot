import json
from pathlib import Path
from pprint import pprint

from app.schemas.ticket import SupportTicket
from app.graph.support_graph import SupportGraphBuilder, create_initial_state


def main():
    graph_builder = SupportGraphBuilder()
    graph = graph_builder.build()

    test_tickets = [
        {
            "ticket_id": "TICKET_201",
            "customer_message": "My order was delayed by 90 minutes and one item was missing. I want a refund.",
            "order_id": "ORDER_201",
            "order_value": 18.5,
            "customer_id": "CUST_201",
            "prior_issues_count": 1,
            "promised_eta_minutes": 30,
            "actual_eta_minutes": 120,
            "tags": [],
        },
        {
            "ticket_id": "TICKET_202",
            "customer_message": "The delivery person was threatening and I felt unsafe during the delivery.",
            "order_id": "ORDER_202",
            "order_value": 42.0,
            "customer_id": "CUST_202",
            "prior_issues_count": 0,
            "promised_eta_minutes": 25,
            "actual_eta_minutes": 30,
            "tags": [],
        },
        {
            "ticket_id": "TICKET_203",
            "customer_message": "I was charged twice for the same order. Please help.",
            "order_id": "ORDER_203",
            "order_value": 120.0,
            "customer_id": "CUST_203",
            "prior_issues_count": 0,
            "promised_eta_minutes": 20,
            "actual_eta_minutes": 20,
            "tags": [],
        },
    ]

    results = []

    for ticket_payload in test_tickets:
        ticket = SupportTicket(**ticket_payload)
        final_state = graph.invoke(create_initial_state(ticket))

        result_summary = {
            "ticket_id": ticket.ticket_id,
            "classification": final_state["classification"],
            "severity": final_state["severity"],
            "resolution": final_state["resolution"],
            "retrieved_policies": [p["name"] for p in final_state["retrieved_policies"]],
            "actions": final_state["actions"],
        }

        results.append(result_summary)

        print("\n" + "=" * 100)
        print(f"RESULT FOR {ticket.ticket_id}")
        print("=" * 100)
        pprint(result_summary)

        print("\nACTION TRACE:")
        for step in final_state["trace"]:
            print(step)

    summary = {
        "total_cases": len(results),
        "results": results,
    }

    # Save artifact
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    with open(artifacts_dir / "regression_eval.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 100)
    print("REGRESSION TEST SUMMARY")
    print("=" * 100)
    pprint(summary)

    print("\nSaved artifact -> artifacts/regression_eval.json")


if __name__ == "__main__":
    main()