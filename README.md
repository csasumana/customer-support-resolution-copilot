# Customer Support Resolution Copilot (LangGraph Agent)

An agentic AI customer support copilot that classifies support tickets, retrieves relevant policy documents using semantic search, plans grounded resolutions, generates customer-facing responses, and produces auditable action traces.

This project is designed to simulate a production-style support operations workflow rather than a generic chatbot. Instead of only generating text, the system diagnoses the issue, retrieves the most relevant internal policy documents, decides the appropriate operational resolution, and logs every decision made along the way.

---

## Why This Project

Most “AI support bot” demos are just prompt wrappers around an LLM.

This project is different:

- **Issue diagnosis** is separated from **requested remedy**
- **Critical cases** (e.g. safety/fraud) use deterministic routing
- **Standard operational issues** use semantic intent matching
- **Policy retrieval** is grounded in local knowledge documents
- **Resolution planning** is explicit and rule-driven
- **Action traces** make the workflow explainable and auditable
- Optional **Gemini refinement** improves response quality with graceful fallback

This makes the system closer to a real support operations copilot than a simple chatbot.

---

## Key Features

- **LangGraph-based agent workflow orchestration**
- **Hybrid ticket classification**
  - Deterministic overrides for high-risk flows (safety / fraud)
  - Embedding-based semantic intent matching for operational issues
- **Semantic policy retrieval** over local policy documents
- **Grounded resolution planning** (refund / replacement / escalation / apology)
- **Customer response generation**
- **Operational action planning** (queue routing, follow-up tasks, priority setting)
- **Full decision trace / audit log**
- **FastAPI API endpoints**
- **Regression and stress-test evaluation suites**
- **Offline-stable local embedding model support**
- Optional **Gemini refinement node** with safe fallback under quota/rate-limit failures

---

## Problem Framing

Customer support tickets often contain:

1. The **actual issue** (e.g. delayed delivery, missing item, wrong item, payment issue)
2. The **requested remedy** (e.g. refund, escalation)

A common failure mode in naive systems is confusing the requested remedy with the underlying issue.

Example:

> “My order was delayed by 90 minutes and one item was missing. I want a refund.”

The root issue is not “refund request” — it is a combination of:
- `delivery_delay`
- `missing_item`

The final system separates:
- **Issue diagnosis** → what happened?
- **Resolution planning** → what should the business do?

This design improved routing quality and made the system more production-realistic.

---

## Architecture

### High-Level Flow

Customer Ticket  
→ Hybrid Classifier  
→ Policy Retrieval  
→ LangGraph Workflow Routing  
→ Resolution Planning  
→ Customer Response Generation  
→ Action Planning  
→ Decision Trace / Audit Log

### Routing Design

#### 1) Deterministic Critical Routing
Used for:
- `safety_issue`
- `fraud_risk`

These are intentionally rule-based because high-risk operational flows should not rely only on semantic similarity.

#### 2) Semantic Operational Classification
Used for:
- `delivery_delay`
- `missing_item`
- `wrong_item`
- `payment_issue`
- `general_complaint`

This uses embedding-based semantic similarity against intent exemplars to improve robustness on paraphrased customer messages.

#### 3) Policy-Grounded Resolution
The system retrieves the most relevant policy documents and uses those to decide:
- refund
- partial refund
- replacement
- escalation
- apology / close
- ask for more information

#### 4) Explainability
Every major decision is logged in a structured **trace**, including:
- classification reason
- routing path
- retrieved policies
- resolution decision
- response generation
- action generation

---

## Tech Stack

- **Python**
- **FastAPI**
- **LangGraph**
- **SentenceTransformers**
- **Local semantic retrieval**
- **Gemini API** (optional refinement layer)
- **JSON-based local policy store**
- **VS Code / PowerShell**

---

## Project Structure

```text
customer-support-resolution-copilot/
│
├── app/
│   ├── agents/
│   │   ├── action_agent.py
│   │   ├── classifier_agent.py
│   │   ├── planner_agent.py
│   │   ├── response_agent.py
│   │   └── workflow.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── prompts.py
│   │
│   ├── generation/
│   │   └── gemini_refiner.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   └── support_graph.py
│   │
│   ├── retrieval/
│   │   ├── embedder.py
│   │   ├── intent_matcher.py
│   │   ├── policy_loader.py
│   │   └── policy_retriever.py
│   │
│   ├── schemas/
│   │   ├── response.py
│   │   └── ticket.py
│   │
│   └── tools/
│       └── logging_tools.py
│
├── data/
│   ├── policies/
│   │   ├── delivery_policy.txt
│   │   ├── escalation_policy.txt
│   │   └── refund_policy.txt
│   │
│   └── tickets/
│       └── support_tickets.json
│
├── tests/
│   ├── eval_cases.json
│   └── stress_test_cases.json
│
├── artifacts/
│   ├── regression_eval.json
│   └── stress_eval.json
│
├── test_day1.py
├── test_day2.py
├── test_day3_langgraph.py
├── test_batch_eval.py
├── test_stress_eval.py
├── requirements.txt
└── README.md

text```
---
Example API Output

Example response from the support resolution API:

{
  "ticket_id": "TICKET_API_001",
  "classification": "safety_issue",
  "severity": "critical",
  "retrieved_policies": [
    "escalation_policy.txt",
    "delivery_policy.txt"
  ],
  "resolution": "escalate_to_specialist",
  "customer_response": "We’re sorry for the inconvenience. Your issue requires specialist review, and our team has escalated it for priority handling. We’ll follow up with you shortly.",
  "actions": [
    "assign_queue:safety_ops_team",
    "set_priority:critical",
    "create_followup_task:specialist_review",
    "create_internal_ticket_note"
  ],
  "trace": [
    {
      "step": "classification",
      "decision": "safety_issue | severity=critical",
      "reason": "Critical safety language detected"
    },
    {
      "step": "urgent_routing",
      "decision": "critical_ticket_routed_to_urgent_path",
      "reason": "Severity is critical, forcing urgent escalation path before planning"
    },
    {
      "step": "retrieval",
      "decision": "retrieved_top_2_policies",
      "reason": "Retrieved ['escalation_policy.txt', 'delivery_policy.txt']"
    },
    {
      "step": "resolution_planning",
      "decision": "escalate_to_specialist",
      "reason": "Fraud or safety issues require immediate escalation per policy"
    }
  ]
}
Evaluation

This project includes two evaluation layers:

1) Regression Evaluation

A small deterministic suite that verifies:

workflow correctness
routing behavior
sensible resolution selection
trace generation
policy retrieval behavior

Saved artifact:

artifacts/regression_eval.json
2) Stress Evaluation

A paraphrase-oriented robustness suite that checks whether the classifier still behaves sensibly when the same intent is phrased differently.

Saved artifact:

artifacts/stress_eval.json
Current Stress-Test Result
Stress classification accuracy: 87.5% (7/8)

This was intentionally not over-optimized to 100% to avoid overfitting to a tiny synthetic stress set.

Design Decisions / What I Learned
1) Issue vs Remedy Separation

A key lesson from this project was that customer messages often contain both:

the operational issue
the requested outcome

Treating “refund request” as a primary class caused misrouting.

The final system separates:

Issue diagnosis
Resolution planning

This improved routing quality and made the workflow more realistic.

2) Hybrid > Pure Rules or Pure LLM

A pure keyword classifier was too brittle.
A pure semantic classifier was too aggressive.

The final design uses:

deterministic overrides for critical/high-risk flows
semantic matching for non-critical operational issues

This was the best balance of:

reliability
robustness
explainability
testability
3) Traceability Matters

The most valuable production-style feature in this project is the action trace.

It makes the system:

debuggable
auditable
interview-friendly
easier to improve systematically
How to Run
1) Create and activate virtual environment
python -m venv .venv

Windows PowerShell

.venv\Scripts\Activate.ps1
2) Install dependencies
pip install -r requirements.txt
3) Run FastAPI server
uvicorn app.api.main:app --reload

Open:

API docs: http://127.0.0.1:8000/docs
Test Scripts
Run core regression flow
python test_day3_langgraph.py
Run stress evaluation
python test_stress_eval.py
Run batch evaluation
python test_batch_eval.py


Current Limitations

This project is intentionally a strong portfolio-grade prototype, not a full production deployment.

Current limitations:

Local JSON/text policy store instead of DB-backed policy management
Small synthetic evaluation suite
No human-in-the-loop approval workflow
No historical customer memory / CRM integration
No confidence calibration endpoint
No real ticketing backend integration (e.g. Zendesk / Freshdesk)
Future Improvements

Potential v2 upgrades:

Expand policy corpus with more realistic support documents
Add confidence score / routing mode to API responses
Introduce reranking for policy retrieval
Add human approval step before high-impact actions
Store ticket history in PostgreSQL
Add real support platform integration
Build a lightweight internal operations dashboard
Add richer evaluation set with real anonymized support-style data
