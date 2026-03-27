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
