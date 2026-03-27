import json
from pathlib import Path
from pprint import pprint

from app.schemas.ticket import SupportTicket
from app.graph.support_graph import SupportGraphBuilder, create_initial_state


BASE_DIR = Path(__file__).resolve().parent
TICKETS_PATH = BASE_DIR / "data" / "tickets" / "support_tickets.json"
EVAL_CASES_PATH = BASE_DIR / "tests" / "eval_cases.json"


def main():
    tickets_data = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))
    eval_cases = json.loads(EVAL_CASES_PATH.read_text(encoding="utf-8"))

    ticket_map = {ticket["ticket_id"]: ticket for ticket in tickets_data}
    eval_map = {case["ticket_id"]: case for case in eval_cases}

    graph_builder = SupportGraphBuilder()
    graph = graph_builder.build()

    results = []
    classification_correct = 0
    resolution_correct = 0

    for ticket_id, ticket_data in ticket_map.items():
        ticket = SupportTicket(**ticket_data)
        result = graph.invoke(create_initial_state(ticket))

        expected = eval_map.get(ticket_id, {})
        expected_classification = expected.get("expected_classification")
        expected_resolution = expected.get("expected_resolution")

        actual_classification = result["classification"]
        actual_resolution = result["resolution"]

        classification_ok = actual_classification == expected_classification
        resolution_ok = actual_resolution == expected_resolution

        if classification_ok:
            classification_correct += 1
        if resolution_ok:
            resolution_correct += 1

        results.append(
            {
                "ticket_id": ticket_id,
                "expected_classification": expected_classification,
                "actual_classification": actual_classification,
                "classification_correct": classification_ok,
                "expected_resolution": expected_resolution,
                "actual_resolution": actual_resolution,
                "resolution_correct": resolution_ok,
                "retrieved_policies": [p["name"] for p in result["retrieved_policies"]],
            }
        )

    total = len(results)

    summary = {
        "total_cases": total,
        "classification_accuracy": round(classification_correct / total, 4) if total else 0.0,
        "resolution_accuracy": round(resolution_correct / total, 4) if total else 0.0,
        "results": results,
    }

    print("\n" + "=" * 100)
    print("BATCH EVALUATION SUMMARY")
    print("=" * 100)
    pprint(summary)


if __name__ == "__main__":
    main()