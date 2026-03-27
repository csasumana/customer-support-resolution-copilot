import json
from pathlib import Path

from fastapi import APIRouter
from app.schemas.ticket import SupportTicket
from app.schemas.response import SupportAgentResponse
from app.graph.support_graph import SupportGraphBuilder, create_initial_state

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TICKETS_PATH = BASE_DIR / "data" / "tickets" / "support_tickets.json"
EVAL_CASES_PATH = BASE_DIR / "tests" / "eval_cases.json"
STRESS_PATH = BASE_DIR / "tests" / "stress_test_cases.json"

graph_builder = SupportGraphBuilder()
support_graph = graph_builder.build()


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Customer Support Resolution Copilot API is running"}


@router.post("/support/run", response_model=SupportAgentResponse)
def run_support_workflow(ticket: SupportTicket):
    initial_state = create_initial_state(ticket)
    result = support_graph.invoke(initial_state)

    return SupportAgentResponse(
        ticket_id=ticket.ticket_id,
        classification=result["classification"],
        severity=result["severity"],
        retrieved_policies=[p["name"] for p in result["retrieved_policies"]],
        resolution=result["resolution"],
        customer_response=result["customer_response"],
        actions=result["actions"],
        trace=result["trace"],
    )


@router.post("/support/batch-eval")
def run_batch_eval():
    tickets_data = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))
    eval_cases = json.loads(EVAL_CASES_PATH.read_text(encoding="utf-8"))

    ticket_map = {ticket["ticket_id"]: ticket for ticket in tickets_data}
    eval_map = {case["ticket_id"]: case for case in eval_cases}

    results = []
    classification_correct = 0
    resolution_correct = 0

    for ticket_id, ticket_data in ticket_map.items():
        ticket = SupportTicket(**ticket_data)
        initial_state = create_initial_state(ticket)
        result = support_graph.invoke(initial_state)

        expected = eval_map.get(ticket_id, {})
        expected_classification = expected.get("expected_classification")
        expected_resolution = expected.get("expected_resolution")

        actual_classification = result["classification"]
        actual_resolution = result["resolution"]

        is_classification_correct = actual_classification == expected_classification
        is_resolution_correct = actual_resolution == expected_resolution

        if is_classification_correct:
            classification_correct += 1
        if is_resolution_correct:
            resolution_correct += 1

        results.append(
            {
                "ticket_id": ticket_id,
                "expected_classification": expected_classification,
                "actual_classification": actual_classification,
                "classification_correct": is_classification_correct,
                "expected_resolution": expected_resolution,
                "actual_resolution": actual_resolution,
                "resolution_correct": is_resolution_correct,
                "retrieved_policies": [p["name"] for p in result["retrieved_policies"]],
                "trace": result["trace"],
            }
        )

    total = len(results)

    return {
        "evaluation_type": "regression_suite",
        "total_cases": total,
        "classification_accuracy": round(classification_correct / total, 4) if total else 0.0,
        "resolution_accuracy": round(resolution_correct / total, 4) if total else 0.0,
        "results": results,
    }


@router.post("/support/stress-eval")
def run_stress_eval():
    stress_cases = json.loads(STRESS_PATH.read_text(encoding="utf-8"))

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
        initial_state = create_initial_state(ticket)
        result = support_graph.invoke(initial_state)

        actual_classification = result["classification"]
        is_classification_correct = actual_classification == expected_classification

        if is_classification_correct:
            classification_correct += 1

        results.append(
            {
                "ticket_id": case["ticket_id"],
                "expected_classification": expected_classification,
                "actual_classification": actual_classification,
                "classification_correct": is_classification_correct,
                "resolution": result["resolution"],
                "retrieved_policies": [p["name"] for p in result["retrieved_policies"]],
                "trace": result["trace"],
            }
        )

    total = len(results)

    return {
        "evaluation_type": "stress_suite",
        "total_cases": total,
        "stress_classification_accuracy": round(classification_correct / total, 4) if total else 0.0,
        "results": results,
    }