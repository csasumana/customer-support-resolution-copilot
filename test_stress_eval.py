import json
from pathlib import Path
from pprint import pprint
from app.schemas.ticket import SupportTicket
from app.graph.support_graph import SupportGraphBuilder, create_initial_state


BASE_DIR = Path(__file__).resolve().parent
STRESS_PATH = BASE_DIR / "tests" / "stress_test_cases.json"


def main():
    stress_cases = json.loads(STRESS_PATH.read_text(encoding="utf-8"))

    graph_builder = SupportGraphBuilder()
    graph = graph_builder.build()

    results = []
    classification_correct = 0

    for case in stress_cases:
        expected_classification = case["expected_classification"]

        ticket_payload = {
            "ticket_id": case["ticket_id"],
            "customer_message": case["customer_message"],
            "order_id": case["order_id"],
            "order_value": case["order_value"],
            "customer_id": case["customer_id"],
            "prior_issues_count": case["prior_issues_count"],
            "promised_eta_minutes": case["promised_eta_minutes"],
            "actual_eta_minutes": case["actual_eta_minutes"],
            "tags": [],
        }

        ticket = SupportTicket(**ticket_payload)
        result = graph.invoke(create_initial_state(ticket))

        actual_classification = result["classification"]
        classification_ok = actual_classification == expected_classification

        if classification_ok:
            classification_correct += 1

        results.append(
            {
                "ticket_id": case["ticket_id"],
                "expected_classification": expected_classification,
                "actual_classification": actual_classification,
                "classification_correct": classification_ok,
                "resolution": result["resolution"],
                "retrieved_policies": [p["name"] for p in result["retrieved_policies"]],
            }
        )

    total = len(results)

    summary = {
        "total_cases": total,
        "stress_classification_accuracy": round(classification_correct / total, 4) if total else 0.0,
        "results": results,
    }

    print("\n" + "=" * 100)
    print("STRESS TEST SUMMARY")
    print("=" * 100)
    print(summary)
  
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    with open(artifacts_dir / "stress_eval.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nSaved artifact -> artifacts/stress_eval.json")
if __name__ == "__main__":
    main()