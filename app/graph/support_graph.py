from typing import Literal

from langgraph.graph import StateGraph, END

from app.graph.state import SupportAgentState
from app.schemas.ticket import SupportTicket
from app.agents.classifier_agent import ClassifierAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.response_agent import ResponseAgent
from app.agents.action_agent import ActionAgent
from app.retrieval.policy_retriever import PolicyRetriever
from app.tools.logging_tools import log_action
from app.generation.gemini_refiner import GeminiResponseRefiner


class SupportGraphBuilder:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.retriever = PolicyRetriever()
        self.planner = PlannerAgent()
        self.responder = ResponseAgent()
        self.action_agent = ActionAgent()
        self.gemini_refiner = GeminiResponseRefiner()

    # ----------------------------
    # Node 1: Classification
    # ----------------------------
    def classify_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]

        classification, severity, classify_reason = self.classifier.classify(ticket)

        state["classification"] = classification
        state["severity"] = severity

        log_action(
            state["trace"],
            step="classification",
            decision=f"{classification} | severity={severity}",
            reason=classify_reason,
        )

        return state

    # ----------------------------
    # Conditional Router
    # ----------------------------
    def route_after_classification(self, state: SupportAgentState) -> Literal["retrieve_policies", "urgent_escalation"]:
        if state["severity"] == "critical":
            return "urgent_escalation"
        return "retrieve_policies"

    # ----------------------------
    # Node 2A: Policy Retrieval
    # ----------------------------
    def retrieve_policies_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]

        retrieved_policies = self.retriever.retrieve(ticket.customer_message, top_k=2)
        state["retrieved_policies"] = retrieved_policies

        log_action(
            state["trace"],
            step="retrieval",
            decision=f"retrieved_top_{len(retrieved_policies)}_policies",
            reason=f"Retrieved {[p['name'] for p in retrieved_policies]}",
        )

        return state

    # ----------------------------
    # Node 2B: Urgent Escalation Path
    # ----------------------------
    def urgent_escalation_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]

        retrieved_policies = self.retriever.retrieve(ticket.customer_message, top_k=2)
        state["retrieved_policies"] = retrieved_policies

        log_action(
            state["trace"],
            step="urgent_routing",
            decision="critical_ticket_routed_to_urgent_path",
            reason="Severity is critical, forcing urgent escalation path before planning",
        )

        log_action(
            state["trace"],
            step="retrieval",
            decision=f"retrieved_top_{len(retrieved_policies)}_policies",
            reason=f"Retrieved {[p['name'] for p in retrieved_policies]}",
        )

        return state

    # ----------------------------
    # Node 3: Resolution Planning
    # ----------------------------
    def plan_resolution_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]
        classification = state["classification"]
        severity = state["severity"]
        retrieved_policies = state["retrieved_policies"]

        resolution, resolution_reason = self.planner.plan_resolution(
            ticket=ticket,
            classification=classification,
            severity=severity,
            retrieved_policies=retrieved_policies,
        )

        state["resolution"] = resolution

        log_action(
            state["trace"],
            step="resolution_planning",
            decision=resolution,
            reason=resolution_reason,
        )

        return state

    # ----------------------------
    # Node 4: Base Customer Response
    # ----------------------------
    def generate_response_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]
        resolution = state["resolution"]
        classification = state["classification"]

        base_response, response_reason = self.responder.generate_response(
            ticket=ticket,
            resolution=resolution,
            classification=classification,
        )

        state["customer_response"] = base_response

        log_action(
            state["trace"],
            step="response_generation",
            decision="customer_response_created",
            reason=response_reason,
        )

        return state

    # ----------------------------
    # Node 5: Gemini Refinement
    # ----------------------------
    def refine_response_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]
        classification = state["classification"]
        resolution = state["resolution"]
        base_response = state["customer_response"]

        final_response, refine_reason = self.gemini_refiner.refine_response(
            customer_message=ticket.customer_message,
            classification=classification,
            resolution=resolution,
            base_response=base_response,
        )

        state["customer_response"] = final_response

        log_action(
            state["trace"],
            step="response_refinement",
            decision="gemini_refinement_attempted",
            reason=refine_reason,
        )

        return state

    # ----------------------------
    # Node 6: Action Planning
    # ----------------------------
    def generate_actions_node(self, state: SupportAgentState) -> SupportAgentState:
        ticket = state["ticket"]
        classification = state["classification"]
        severity = state["severity"]
        resolution = state["resolution"]

        actions, actions_reason = self.action_agent.generate_actions(
            ticket=ticket,
            classification=classification,
            severity=severity,
            resolution=resolution,
        )

        state["actions"] = actions

        log_action(
            state["trace"],
            step="action_planning",
            decision=f"generated_{len(actions)}_actions",
            reason=actions_reason,
        )

        return state

    # ----------------------------
    # Build Graph
    # ----------------------------
    def build(self):
        graph = StateGraph(SupportAgentState)

        graph.add_node("classify", self.classify_node)
        graph.add_node("retrieve_policies", self.retrieve_policies_node)
        graph.add_node("urgent_escalation", self.urgent_escalation_node)
        graph.add_node("plan_resolution", self.plan_resolution_node)
        graph.add_node("generate_response", self.generate_response_node)
        graph.add_node("refine_response", self.refine_response_node)
        graph.add_node("generate_actions", self.generate_actions_node)

        graph.set_entry_point("classify")

        graph.add_conditional_edges(
            "classify",
            self.route_after_classification,
            {
                "retrieve_policies": "retrieve_policies",
                "urgent_escalation": "urgent_escalation",
            },
        )

        graph.add_edge("retrieve_policies", "plan_resolution")
        graph.add_edge("urgent_escalation", "plan_resolution")
        graph.add_edge("plan_resolution", "generate_response")
        graph.add_edge("generate_response", "refine_response")
        graph.add_edge("refine_response", "generate_actions")
        graph.add_edge("generate_actions", END)

        return graph.compile()


def create_initial_state(ticket: SupportTicket) -> SupportAgentState:
    return {
        "ticket": ticket,
        "classification": None,
        "severity": None,
        "retrieved_policies": [],
        "resolution": None,
        "customer_response": None,
        "actions": [],
        "trace": [],
    }