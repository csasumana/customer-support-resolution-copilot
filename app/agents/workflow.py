from app.agents.classifier_agent import ClassifierAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.response_agent import ResponseAgent
from app.agents.action_agent import ActionAgent
from app.retrieval.policy_retriever import PolicyRetriever
from app.tools.logging_tools import log_action
from app.graph.state import SupportAgentState
from app.schemas.ticket import SupportTicket
from app.generation.gemini_refiner import GeminiResponseRefiner


class SupportWorkflow:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.retriever = PolicyRetriever()
        self.planner = PlannerAgent()
        self.responder = ResponseAgent()
        self.action_agent = ActionAgent()
        self.gemini_refiner = GeminiResponseRefiner()

    def run(self, ticket: SupportTicket) -> SupportAgentState:
        state: SupportAgentState = {
            "ticket": ticket,
            "classification": None,
            "severity": None,
            "retrieved_policies": [],
            "resolution": None,
            "customer_response": None,
            "actions": [],
            "trace": [],
        }

        # Step 1: Classify
        classification, severity, classify_reason = self.classifier.classify(ticket)
        state["classification"] = classification
        state["severity"] = severity
        log_action(
            state["trace"],
            step="classification",
            decision=f"{classification} | severity={severity}",
            reason=classify_reason,
        )

        # Step 2: Retrieve policies
        retrieved_policies = self.retriever.retrieve(ticket.customer_message, top_k=2)
        state["retrieved_policies"] = retrieved_policies
        log_action(
            state["trace"],
            step="retrieval",
            decision=f"retrieved_top_{len(retrieved_policies)}_policies",
            reason=f"Retrieved {[p['name'] for p in retrieved_policies]}",
        )

        # Step 3: Plan resolution
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

        # Step 4: Generate deterministic response
        base_response, response_reason = self.responder.generate_response(
            ticket=ticket,
            resolution=resolution,
            classification=classification,
        )

        # Step 5: Refine with Gemini (safe enhancement)
        final_response, refine_reason = self.gemini_refiner.refine_response(
            customer_message=ticket.customer_message,
            classification=classification,
            resolution=resolution,
            base_response=base_response,
        )

        state["customer_response"] = final_response

        log_action(
            state["trace"],
            step="response_generation",
            decision="customer_response_created",
            reason=response_reason,
        )

        log_action(
            state["trace"],
            step="response_refinement",
            decision="gemini_refinement_attempted",
            reason=refine_reason,
        )

        # Step 6: Generate actions
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